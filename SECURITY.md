# Security

## Reporting a vulnerability

Please report it privately, through
[a security advisory](https://github.com/adrianmg/noted/security/advisories/new),
not in a public issue. You'll hear back within a few days.

## What you install

- Every release's files are listed, with their SHA-256, in its `SHA256SUMS`;
  the install scripts and the npm package check each build against it.
- The npm package, [@adrianmg/noted](https://www.npmjs.com/package/@adrianmg/noted),
  is published by this repository's [npm workflow](.github/workflows/npm.yml)
  with a provenance statement: `npm audit signatures` checks it.
- The npm package holds each system's build, a small Node launcher
  (`bin/noted`) and an install script (`install.js`) that, under npm on
  macOS and Linux, puts this system's build in the launcher's place so
  `noted` starts with no Node in between. Neither downloads anything.
- noted itself makes no network connections: it reads and writes your notes,
  plain Markdown files in a folder you choose. (Its Help menu can open
  noted.computer, in your browser.)
