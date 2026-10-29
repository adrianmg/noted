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

## Network requests

noted has no telemetry, analytics or crash reporting. Its only built-in
network request is the update check, added in 1.3.0 and on by default.

- **What:** an HTTPS request, with `curl`, for
  `https://noted.computer/download/latest/VERSION`: a static text file on
  Vercel holding just the latest version number, such as `1.4.0`. It loads
  none of the website's scripts.
- **When:** shortly after noted starts, then not again for 24 hours after a
  successful check (a failed one is retried at the next launch). Noted ▸
  Check for updates (`^O`) also checks when no newer version is shown.
- **What's sent:** noted adds no identifier, no version of its own and
  nothing from your notes. Like any web request, Vercel still sees your IP
  address and standard headers, including curl's User-Agent with its
  version, under Vercel's own logging policies.
- **Nothing installs itself:** a newer version only shows a notice.

To turn it off, uncheck Options ▸ Automatically check for updates. To skip
even the first check, add `updates = off` to the settings file before
launching noted: `$XDG_CONFIG_HOME/noted/settings` if that's set, else
`~/.config/noted/settings` (`%APPDATA%\noted\settings` on Windows).
Checking by hand still works.

The Help menu and the update notice can open noted.computer or GitHub
in your browser; those pages, which on noted.computer include Vercel Web
Analytics, are loaded by the browser, not noted.

Images in notes are read as files, as the notes themselves are. noted
doesn't fetch an image a note names by a web or network address
(`https://…`, `\\server\share\…`, `file://server/…`), so a note can't
make noted, or Windows on its behalf, contact a server. Open image hands
the file to your system's app for it.
