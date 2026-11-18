# Blog content

One Markdown file is one note. The file name is the URL: `first-note.md` is
served at `/blog/first-note`.

Frontmatter:

```yaml
---
title: The first note
date: 2026-11-18
draft: true
description: Optional, one line.
---
```

`draft: true` is the default. Nothing is published by accident; set
`draft: false` when the note is ready.

Files whose name starts with an underscore are ignored, which is why this file
does not appear as a post.
