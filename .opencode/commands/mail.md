---
description: Read the DeepSeek1 / DeepSeek2 mailbox and take the newest job
---

The mailbox between DeepSeek1 (the main session) and DeepSeek2 (this session).
Work in `/Users/thomaskelly/developer/curve-lab`.

1. Read only the newest entries, never the whole transcript:

   ```sh
   .venv/bin/python scripts/mailbox.py --read 1
   ```

2. Act on the newest **job** in `archive/notes/deep-to-side.md`. You own only
   the files that entry names. If a fix is needed elsewhere, write the fault and
   the file in your reply; do not edit it. The operator may be working in the
   same tree, so do not touch `app/prisma/dev.db`.

3. Reply in `archive/notes/side-to-deep.md`, appended at the bottom, in this
   shape:

   ```
   ## YYYY-MM-DD HH:MM — one-line subject
   Job: what you were asked to do, in one line
   Done: what you did
   Proved by: the command that shows it
   Blocked: what stopped you, or "nothing"
   Next: the next step, or "waiting for DeepSeek1"
   ```

4. Check the shape before you finish:

   ```sh
   .venv/bin/python scripts/mailbox.py --check
   ```

The plain word **mail** means the same thing, in either session, if a slash
command is not available.
