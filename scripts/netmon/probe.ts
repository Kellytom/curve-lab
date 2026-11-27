/**
 * One probe of the service OpenCode talks to.
 *
 * The failure the operator sees is `getaddrinfo ENOTFOUND opencode.ai`, so the
 * probe does the two things that failure sits in: resolve the name, then open a
 * TCP connection on 443. It does not send an HTTP request and it does not log
 * in; a name that resolves and a port that accepts are the link, and that is
 * what "opencode drops" means at this layer.
 */
import { lookup } from "node:dns/promises";
import net from "node:net";

export type Reach = {
  ok: boolean;
  /** Time to resolve the name, in milliseconds. */
  dnsMs: number | null;
  /** Time to open TCP 443, in milliseconds. */
  tcpMs: number | null;
  address: string | null;
  error: string | null;
};

function message(error: unknown): string {
  if (error instanceof Error) {
    const code = (error as NodeJS.ErrnoException).code;
    return code ? `${code}: ${error.message}` : error.message;
  }
  return String(error);
}

function withTimeout<T>(promise: Promise<T>, ms: number, label: string): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`${label} timed out after ${ms} ms`)), ms);
    promise.then(
      (value) => {
        clearTimeout(timer);
        resolve(value);
      },
      (error) => {
        clearTimeout(timer);
        reject(error);
      },
    );
  });
}

function connect(address: string, port: number): Promise<void> {
  return new Promise((resolve, reject) => {
    const socket = net.connect({ host: address, port });
    const finish = (error?: Error): void => {
      socket.destroy();
      if (error) reject(error);
      else resolve();
    };
    socket.once("connect", () => finish());
    socket.once("error", (error) => finish(error));
  });
}

export async function probeHost(host: string, timeoutMs = 5000): Promise<Reach> {
  const started = performance.now();
  let address: string;
  try {
    const found = await withTimeout(lookup(host), timeoutMs, `DNS ${host}`);
    address = found.address;
  } catch (error) {
    return {
      ok: false,
      dnsMs: Math.round(performance.now() - started),
      tcpMs: null,
      address: null,
      error: message(error),
    };
  }

  const dnsMs = Math.round(performance.now() - started);
  const tcpStarted = performance.now();
  try {
    await withTimeout(connect(address, 443), timeoutMs, `TCP ${host}:443`);
  } catch (error) {
    return {
      ok: false,
      dnsMs,
      tcpMs: Math.round(performance.now() - tcpStarted),
      address,
      error: message(error),
    };
  }

  return {
    ok: true,
    dnsMs,
    tcpMs: Math.round(performance.now() - tcpStarted),
    address,
    error: null,
  };
}
