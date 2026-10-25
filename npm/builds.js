'use strict';
// Which of the package's builds runs on this system. pack.mjs puts them in vendor/, from the release's files.

const path = require('path');

const BUILDS = {
  'darwin arm64': 'darwin/noted', // one binary for Apple silicon and Intel
  'darwin x64': 'darwin/noted',
  'linux x64': 'linux-x64/noted', // static: any distribution
  'linux arm64': 'linux-arm64/noted',
  'win32 x64': 'win32-x64/noted.exe',
  'win32 arm64': 'win32-x64/noted.exe', // Windows on Arm runs it emulated
};

exports.build = function build() {
  const file = BUILDS[process.platform + ' ' + process.arch];
  if (!file) throw new Error('no build for ' + process.platform + ' on ' + process.arch + ' yet: https://noted.computer');
  return path.join(__dirname, 'vendor', file);
};
