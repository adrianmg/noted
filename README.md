<p align="center">
	<h1 align="center">
		<img src="https://raw.githubusercontent.com/adrianmg/noted/main/docs/logo.png" alt="noted's logo: a floppy disk" width="128">
		<br>
		noted
	</h1>
	<p align="center">Markdown notes in your terminal, as if they ran on MS-DOS.<br>Opens instantly, saves as you type, keeps every note as a plain Markdown file.</p>
	<p align="center">
		<a href="https://www.npmjs.com/package/@adrianmg/noted"><img src="https://img.shields.io/npm/v/%40adrianmg%2Fnoted?label=npm&color=0000aa" alt="npm version" height="18"></a>
		<a href="https://github.com/adrianmg/noted/releases"><img src="https://img.shields.io/github/v/release/adrianmg/noted?label=release&color=00aaaa" alt="Latest release" height="18"></a>
		<a href="https://noted.computer"><img src="https://img.shields.io/badge/website-noted.computer-ffff55" alt="Website: noted.computer" height="18"></a>
	</p>
</p>

<p align="center">
	<br>
	<img src="https://raw.githubusercontent.com/adrianmg/noted/main/docs/demo.gif" alt="noted starting from the shell: a new note with a task list, ticking a task, the notes list, finding a note as you type, then the Amber theme" width="720">
	<br>
</p>

## Installation

```sh
# npm: macOS, Linux and Windows (Node 18 or newer)
npm install -g @adrianmg/noted

# Homebrew: macOS and Linux
brew tap adrianmg/noted https://github.com/adrianmg/noted
brew trust adrianmg/noted
brew install noted

# Install script: checks the build against the release's checksums
curl -fsSL https://noted.computer/install | sh      # macOS, Linux
irm https://noted.computer/install.ps1 | iex        # Windows, in PowerShell
```

## Usage

```sh
noted                     # a new note, cursor ready
noted buy oat milk        # a new note that starts with those words
noted --theme amber       # turbo, amber, phosphor, charcoal, lime, midnight,
                          # catppuccin, dracula, gruvbox, rosepine, synthwave
noted --dir ~/Notes       # keep notes in another folder this time
noted --path              # print where your notes are
noted --help              # every option
```

## What it does

noted opens on a new note in about 2.5 ms and saves as you type, so there's
no save button and nothing to lose. Each note is a plain Markdown file named
after its first line, in a `Noted` folder in iCloud Drive when it's on, or
else in Documents, where any editor can open it: `noted --path` prints where,
and Noted ▸ Notes folder… moves them elsewhere. Markdown is lit as you type,
finding searches every note as you type, and it all looks like MS-DOS:
pull-down menus, Norton Commander panes and eleven themes. It runs on macOS,
Linux and Windows, in any terminal.

## Keys

| Key | |
|---|---|
| `ESC` | Notes list, and back |
| `⌘F` or `^F` | Find a note, or create one |
| `^N` | New note |
| `^T` | Make a task, tick it |
| `^G` | Insert a table |
| `^D` | Delete the note (to the Trash; `^Z` puts it back) |
| `F10` | Menus |
| `F1` | Every key |
| `^Q` | Exit |

On a PC, read `⌘` as `^` and `⌥` as `ALT`.

## Updating

```sh
npm install -g @adrianmg/noted     # npm
brew upgrade noted                 # Homebrew
```

With the install scripts, run them again.

## Why?

A thought is gone in seconds, and most notes apps take longer than that to
open. noted is a terminal away, ready before you finish pressing Enter, and
leaves you nothing but plain files in a folder you own.

Do you want to know more? [Visit noted.computer](https://noted.computer),
with a live demo and the User's Guide.

## Questions? Ideas? Bugs?

[Open an issue](https://github.com/adrianmg/noted/issues) or hit me
up on [Twitter](https://twitter.com/adrianmg).

This repository holds noted's releases, its Homebrew formula and this README;
the npm package, [@adrianmg/noted](https://www.npmjs.com/package/@adrianmg/noted),
ships the same builds.

## License

Made by [Adrián Mato](https://adrianmato.com). Available under the terms of
the [MIT License](https://github.com/adrianmg/noted/blob/main/LICENSE).
