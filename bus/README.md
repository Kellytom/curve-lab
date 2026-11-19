# The message bus

A small, durable mailbox between agents. One POST to send, one GET to receive,
one POST to acknowledge. The transport is HTTP + JSON; the store is SQLite
through Prisma, in the same database the app already uses.

The mailbox files in `archive/notes/` stay as the human-readable record. The bus
is the transport: a message survives a server restart, and an unacknowledged
message is delivered again.

## Why this shape

The operator asked for an industry-standard way for two AI modules to talk,
without a person carrying messages between them. Four candidates were compared:

- **A2A / JSON-RPC agent-to-agent.** A full protocol with discovery, tasks and
  streaming; more moving parts than two agents on one machine need.
- **MCP (Model Context Protocol).** A standard for exposing tools and resources
  to a model; it is a tool interface, not a durable inbox, and a queue is still
  needed underneath.
- **A plain webhook or a queue service (Redis, SQS).** The right semantics, but
  one more service to run and secure.
- **HTTP + JSON + SQLite through Prisma.** The chosen one: the Astro server and
  the database already exist, and the three routes are the whole protocol. It
  gives a durable, ordered, at-least-once queue with a long-poll for near-push,
  and no second process.

## The message

```json
{
  "id": 42,
  "from": "deepseek1",
  "to": "deepseek2",
  "topic": "job",
  "body": { "text": "hello" },
  "createdAt": "2026-11-19T07:00:00.000Z",
  "attempts": 1
}
```

- `id` is the SQLite row id; ordering per `(from, to)` is this number.
- `topic` is a short string the receiver may switch on (`job`, `status`, ...).
- `body` is any JSON value. The server validates the envelope before it stores
  the row; the body is stored as JSON text.
- `attempts` rises each time the message is delivered.

## Using it from a session

Send:

```sh
node bus/send.mjs --from deepseek1 --to deepseek2 --topic job --body '{"text":"hello"}'
```

Read (the long-poll holds the request for up to 25 s, so it blocks rather than
spins):

```sh
node bus/read.mjs --for deepseek2 --wait 25000
```

Acknowledge:

```sh
node bus/read.mjs --ack 42
```

The client is `bus/client.mjs`; both agents import it, so there is one copy of
the three calls. Set `CURVE_LAB_BUS_URL` when the server is not on `:4321`.

## Adding a third agent

Nothing to register. Use a new name in `--from` and `--to`; the `toAgent` index
is the inbox. A consumer is a loop:

```js
import { ack, read } from "./client.mjs";

for (;;) {
  for (const message of await read({ for: "agent3", wait: 25000 })) {
    handle(message);
    await ack(message.id);
  }
}
```

## Delivery guarantees

- **Durable.** The row is in SQLite, so a server restart does not lose it.
- **Ordered per pair.** Messages from one agent to another come back in row-id
  order.
- **At-least-once.** An unacknowledged message is returned again on the next
  read; a consumer that crashes between read and ack sees it twice.
- **Ack removes it from the inbox.** The row stays as history with `ackedAt`
  set.
- **Validated before storage.** A missing `from`, `to` or `topic`, or a body
  that is not JSON, is refused before a row is written.

## Limits

- **No authentication.** Anyone who can reach the server can send and read.
  Keep it on the local machine or a trusted network.
- **Not exactly-once.** A crash between read and ack redelivers; consumers must
  be idempotent.
- **One recipient per message.** Send to each agent separately; there is no
  fan-out.
- **No retention policy.** Acked rows stay. Prune the table when it grows.
- **A long-poll holds a connection** for up to 30 s. The Astro server has a
  limited concurrency; use a short `--wait` when many readers run at once.
- **No schema registry.** `body` is free JSON; `topic` is a string convention,
  not an enforced contract.
