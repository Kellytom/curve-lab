// The copy buttons on /said/. One job: put that message on the clipboard and say so.
export function mountCopyButtons(root = document) {
  for (const button of root.querySelectorAll("button.copy[data-index]")) {
    button.addEventListener("click", async () => {
      const text = document.getElementById(`said-${button.dataset.index}`);
      if (!text) return;
      try {
        await navigator.clipboard.writeText(text.textContent);
        button.textContent = "copied";
        button.classList.add("ok");
      } catch {
        button.textContent = "copy failed";
      }
      setTimeout(() => {
        button.textContent = "copy";
        button.classList.remove("ok");
      }, 1200);
    });
  }
}

if (typeof document !== "undefined") mountCopyButtons();
