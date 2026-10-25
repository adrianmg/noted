'use strict';
// After npm links `noted` to bin/noted (a Node stand-in), on macOS and Linux this puts this system's build in
// its place: the link then starts noted itself, in a couple of milliseconds, with no Node in between.
//
// Only under npm, which links bin/noted as it is. Other package managers may write a shim that runs it with
// node, which a native file would break; on Windows, npm's .cmd shim does. There the stand-in stays, and it
// works. Anything going wrong here leaves the stand-in too: an install never fails for this.

const fs = require('fs');
const path = require('path');

function main() {
  if (process.platform === 'win32') return;
  if (!/^npm\//.test(process.env.npm_config_user_agent || '')) return;
  let build;
  try {
    build = require('./builds.js').build();
    fs.accessSync(build);
  } catch (e) {
    return;
  }
  const bin = path.join(__dirname, 'bin', 'noted');
  const tmp = bin + '.' + process.pid;
  try {
    // A hard link takes no more room; where there can't be one, a copy.
    try { fs.linkSync(build, tmp); } catch (e) { fs.copyFileSync(build, tmp); }
    fs.chmodSync(tmp, 0o755);
    // Atomic: bin/noted is always one or the other. Run again, it may already be this very file, and
    // rename() leaves both names: the spare one goes.
    fs.renameSync(tmp, bin);
  } catch (e) {
    // The stand-in stays.
  }
  try { fs.unlinkSync(tmp); } catch (e) { /* gone, as it should be */ }
}

main();
