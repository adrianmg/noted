#!/usr/bin/env node
// Makes noted's npm package, @adrianmg/noted, from a release's files: each system's build, checked against the
// release's SHA256SUMS, goes into vendor/ beside the launcher (bin/noted), and `npm pack` writes the tarball
// that `npm publish` sends. Nothing is built here: the package holds the very files the release has.
//
//   node npm/pack.mjs                               # the release of Cargo.toml's version, from noted.computer
//   node npm/pack.mjs --from site/download/v1.0.0   # ...or from a folder with a release's files
//   node npm/pack.mjs --version 1.0.0-rc.1          # those builds as a prerelease, to try the registry first
//   node npm/pack.mjs --out /tmp/npm                # where the tarball goes (else npm/dist)
//
// The package's version is the release's (its VERSION file), or --version: that one, or a prerelease of it.
// Needs Node 18 or newer, npm, and tar (for the Windows .zip, a tar that reads one, or unzip).

import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(HERE);
// Each system's build: the release's archive with it, and where the package keeps it (as builds.js reads it).
const BUILDS = [
  { asset: 'noted-macos-universal.tar.gz', file: 'darwin/noted' },
  { asset: 'noted-linux-x86_64.tar.gz', file: 'linux-x64/noted' },
  { asset: 'noted-linux-aarch64.tar.gz', file: 'linux-arm64/noted' },
  { asset: 'noted-windows-x86_64.zip', file: 'win32-x64/noted.exe' },
];
// The package's own files, from this folder; package.json is written with the version, LICENSE is the repo's.
const OWN = ['README.md', 'builds.js', 'install.js', 'bin/noted'];
const WIN = process.platform === 'win32';

function fail(message) {
  throw new Error(message);
}

function options(argv) {
  const opt = {};
  for (let i = 0; i < argv.length; i++) {
    const m = /^--(from|version|out)$/.exec(argv[i]);
    if (!m || i + 1 >= argv.length) fail('usage: node npm/pack.mjs [--from <folder or URL>] [--version <version>] [--out <folder>]');
    opt[m[1]] = argv[++i];
  }
  return opt;
}

function cargoVersion() {
  let inPackage = false;
  for (const line of fs.readFileSync(path.join(ROOT, 'Cargo.toml'), 'utf8').split('\n')) {
    if (/^\[/.test(line)) inPackage = /^\[package\]\s*$/.test(line);
    const m = inPackage && /^version\s*=\s*"([^"]+)"/.exec(line);
    if (m) return m[1];
  }
  fail('no [package] version in Cargo.toml');
}

async function read(from, name) {
  if (/^https?:\/\//.test(from)) {
    const url = from.replace(/\/+$/, '') + '/' + name;
    const res = await fetch(url);
    if (!res.ok) fail(`couldn't download ${url}: ${res.status}`);
    return Buffer.from(await res.arrayBuffer());
  }
  const file = path.join(from, name);
  if (!fs.existsSync(file)) fail(`no ${file}`);
  return fs.readFileSync(file);
}

function extract(archive, dir) {
  fs.mkdirSync(dir, { recursive: true });
  if (!archive.endsWith('.zip')) {
    execFileSync('tar', ['-xzf', archive, '-C', dir], { stdio: 'inherit' });
    return;
  }
  // bsdtar (macOS, Windows) reads a .zip; GNU tar doesn't, and there unzip does.
  try {
    execFileSync('tar', ['-xf', archive, '-C', dir], { stdio: 'ignore' });
  } catch (e) {
    execFileSync('unzip', ['-o', '-q', archive, '-d', dir], { stdio: 'inherit' });
  }
}

// npm is a .cmd on Windows, which only a shell starts.
function npm(args, cwd) {
  if (!WIN) return execFileSync('npm', args, { cwd, encoding: 'utf8' });
  return execFileSync(['npm', ...args.map((a) => '"' + a + '"')].join(' '), { cwd, encoding: 'utf8', shell: true });
}

async function main() {
  const opt = options(process.argv.slice(2));
  const from = opt.from || `https://noted.computer/download/v${cargoVersion()}`;
  const release = (await read(from, 'VERSION')).toString().trim();
  const version = opt.version || release;
  if (version !== release && !version.startsWith(release + '-')) {
    fail(`${version} is neither the release's version, ${release}, nor a prerelease of it`);
  }
  const sums = new Map();
  for (const line of (await read(from, 'SHA256SUMS')).toString().split('\n')) {
    const m = /^([0-9a-f]{64}) [ *](\S+)$/.exec(line.trim());
    if (m) sums.set(m[2], m[1]);
  }

  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'noted-npm-'));
  try {
    const stage = path.join(tmp, 'package');
    for (const name of OWN) {
      fs.mkdirSync(path.dirname(path.join(stage, name)), { recursive: true });
      fs.copyFileSync(path.join(HERE, name), path.join(stage, name));
    }
    fs.chmodSync(path.join(stage, 'bin', 'noted'), 0o755);
    fs.copyFileSync(path.join(ROOT, 'LICENSE'), path.join(stage, 'LICENSE'));
    const pkg = JSON.parse(fs.readFileSync(path.join(HERE, 'package.json'), 'utf8'));
    pkg.version = version;
    fs.writeFileSync(path.join(stage, 'package.json'), JSON.stringify(pkg, null, 2) + '\n');

    console.log(`${pkg.name}@${version}, from noted ${release}'s files at ${from}:`);
    for (const build of BUILDS) {
      const bytes = await read(from, build.asset);
      const want = sums.get(build.asset);
      if (!want) fail(`${build.asset} isn't in SHA256SUMS`);
      if (createHash('sha256').update(bytes).digest('hex') !== want) fail(`${build.asset} doesn't match its checksum`);
      const archive = path.join(tmp, build.asset);
      fs.writeFileSync(archive, bytes);
      const out = path.join(tmp, 'unpacked', build.asset);
      extract(archive, out);
      const exe = path.join(out, path.basename(build.file));
      if (!fs.existsSync(exe)) fail(`no ${path.basename(build.file)} in ${build.asset}`);
      const dest = path.join(stage, 'vendor', build.file);
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.copyFileSync(exe, dest);
      fs.chmodSync(dest, 0o755);
      console.log(`  ${build.asset}: checksum matches, vendor/${build.file}`);
    }

    // The build for this system, found as the package finds it, answers with the release's version.
    let mine = null;
    try { mine = createRequire(import.meta.url)(path.join(stage, 'builds.js')).build(); } catch (e) { /* not one of them */ }
    if (mine) {
      const said = execFileSync(mine, ['--version'], { encoding: 'utf8' }).trim();
      if (!said.includes(release)) fail(`vendor's build for this system says "${said}", not ${release}`);
      console.log(`  ${path.relative(fs.realpathSync(stage), mine)} --version: ${said}`);
    }

    const dest = path.resolve(opt.out || path.join(HERE, 'dist'));
    fs.mkdirSync(dest, { recursive: true });
    const [made] = JSON.parse(npm(['pack', '--json', '--pack-destination', dest], stage));
    const mb = (n) => (n / 1e6).toFixed(1) + ' MB';
    // Relative, as a path npm can't take for a GitHub "user/repo".
    const abs = path.join(dest, made.filename), rel = path.relative(process.cwd(), abs);
    const tarball = path.isAbsolute(rel) || rel.startsWith('..') ? abs : '.' + path.sep + rel;
    console.log(`${tarball}: ${mb(made.size)}, ${mb(made.unpackedSize)} unpacked, ${made.entryCount} files`);
    console.log(`  ${made.integrity}`);
    console.log(`Publish it from an npm account that may publish ${pkg.name}:`);
    console.log(`  npm publish ${tarball}${version === release ? '' : ' --tag next'}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}

main().catch((e) => {
  console.error('pack: ' + e.message);
  process.exit(1);
});
