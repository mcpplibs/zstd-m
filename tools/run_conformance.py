#!/usr/bin/env python3
"""Run Zstandard's own examples (of the release) against compat.zstd 1.5.7, the
library this wrapper exports.

The release tarball is downloaded once into target/upstream and checked
against upstream/documents.json. simple_compression.c, simple_decompression.c,
streaming_compression.c, streaming_decompression.c and their common.h are
copied unchanged into target/conformance/examples, and a project there builds
them as C over compat.zstd (a C program includes <zstd.h>; the module's own
tests are tests/*.cpp). The release's README.md is compressed in one shot and
decoded in memory, then compressed as a stream and decoded as a stream; the
decoded bytes must equal the original.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import urllib.request

MANIFEST = '''[package]
name        = "zstd-conformance"
version     = "1.5.7"
description = "Zstandard 1.5.7's examples over compat.zstd (tools/run_conformance.py)"

[targets.simple_compression]
kind = "bin"
main = "examples/simple_compression.c"

[targets.simple_decompression]
kind = "bin"
main = "examples/simple_decompression.c"

[targets.streaming_compression]
kind = "bin"
main = "examples/streaming_compression.c"

[targets.streaming_decompression]
kind = "bin"
main = "examples/streaming_decompression.c"

[build]
c_standard = "c11"
sources    = []
# common.h reads file sizes with stat() and off_t, which ISO C does not declare.
cflags     = ["-D_POSIX_C_SOURCE=200809L"]

[dependencies]
compat.zstd = "1.5.7"
'''


def fetch(root: Path) -> Path:
    pins = json.loads((root / 'upstream/documents.json').read_text(encoding='utf-8'))
    cache = root / 'target/upstream'
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / 'zstd-release.tar.gz'
    if not archive.exists() or hashlib.sha256(archive.read_bytes()).hexdigest() != pins['upstream_sha256']:
        print('+ fetch', pins['upstream'], flush=True)
        with urllib.request.urlopen(pins['upstream'], timeout=120) as response:
            archive.write_bytes(response.read())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != pins['upstream_sha256']:
        sys.exit(f'upstream archive checksum {digest} != {pins["upstream_sha256"]}')
    with tarfile.open(archive) as tar:
        top = tar.getmembers()[0].name.split('/')[0]
        if not (cache / top).exists():
            tar.extractall(cache, filter='data')
    return cache / top


def run(command, cwd, **kwargs):
    print('+', ' '.join(map(str, command)), flush=True)
    return subprocess.run(command, cwd=cwd, check=True, **kwargs)


EXAMPLES = ('simple_compression', 'simple_decompression', 'streaming_compression', 'streaming_decompression')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mcpp', default='mcpp')
    parser.add_argument('--toolchain')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    upstream = fetch(root)
    work = root / 'target/conformance'
    shutil.rmtree(work, ignore_errors=True)
    (work / 'examples').mkdir(parents=True)
    for name in [e + '.c' for e in EXAMPLES] + ['common.h']:
        shutil.copyfile(upstream / 'examples' / name, work / 'examples' / name)
    (work / 'mcpp.toml').write_text(MANIFEST, encoding='utf-8')
    build = [args.mcpp, 'build', '--release']
    if args.toolchain:
        build += ['--toolchain', args.toolchain]
    run(build, work)
    binaries = {p.stem: p for p in (work / 'target').rglob('*') if p.is_file() and p.stem in EXAMPLES
                and p.suffix in ('', '.exe')}
    missing = [e for e in EXAMPLES if e not in binaries]
    if missing:
        sys.exit(f'did not build: {missing}')
    sample = work / 'sample.txt'
    shutil.copyfile(upstream / 'README.md', sample)
    run([binaries['simple_compression'], sample.name], work)
    run([binaries['simple_decompression'], sample.name + '.zst'], work)
    run([binaries['streaming_compression'], sample.name], work)
    decoded = run([binaries['streaming_decompression'], sample.name + '.zst'], work, capture_output=True).stdout
    if sys.platform == 'win32':  # the example writes to stdout, which Windows opens in text mode
        decoded = decoded.replace(b'\r\n', b'\n')
    if decoded != sample.read_bytes():
        sys.exit('streaming_decompression did not restore the sample')
    print('Zstandard 1.5.7: the examples round-trip over compat.zstd', flush=True)


if __name__ == '__main__':
    main()
