# zstd

> Zstandard, the fast lossless compression library, through C++23 modules.

**English** · [简体中文](README.zh.md) · [Upstream](https://github.com/facebook/zstd) · [Releases](https://github.com/mcpplibs/zstd-m/releases) · [mcpp](https://github.com/mcpp-community/mcpp) · [Index](https://github.com/mcpplibs/mcpp-index)

[![C++23](https://img.shields.io/badge/C%2B%2B-23-blue.svg)](https://en.cppreference.com/w/cpp/23)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![mcpp-community](https://img.shields.io/badge/mcpp--community-mwrap-blue)](https://github.com/mcpp-community)
[![CI](https://github.com/mcpplibs/zstd-m/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mcpplibs/zstd-m/actions/workflows/ci.yml)

The upstream API is unchanged. `ZSTD_compress`, `ZSTD_compress2`,
`ZSTD_decompressStream`, `ZSTD_CCtx`, `ZSTD_cParameter` and its enumerators,
and the error codes of `<zstd_errors.h>` are the upstream entities, in the
global namespace where upstream declares them. The library is `compat.zstd`
1.5.7. The constant macros are C++ constants. Upstream's own examples
round-trip on every CI run over the same library.

## Modules

- `import mcpplibs.mwrap.zstd;`: the stable API of `<zstd.h>` and the error codes of `<zstd_errors.h>`, re-exporting the macros module
- `import mcpplibs.mwrap.zstd.macros;`: `ZSTD_CLEVEL_DEFAULT`, `ZSTD_CONTENTSIZE_ERROR`, `ZSTD_MAGICNUMBER`, `ZSTD_VERSION_NUMBER` … in `mcpplibs::mwrap::zstd::macros`
- `#include <mwrap/zstd/macros.hpp>`: `ZSTD_COMPRESSBOUND(size)`, the bound as a constant expression

> More Modules API -> [Usage and API](docs/usage.md)

## Getting started

```sh
mcpp new squeeze --template mcpplibs.mwrap.zstd@1.5.7
cd squeeze
mcpp run
```

The default template compresses a text at two levels with a checksum, then
restores it and prints the sizes.

```toml
[dependencies]
"mcpplibs.mwrap.zstd" = "1.5.7"
```

```cpp
import std;
import mcpplibs.mwrap.zstd;

namespace z = mcpplibs::mwrap::zstd::macros;

int main() {
    std::string text(10000, 'z'), frame(ZSTD_compressBound(text.size()), '\0');
    const auto n = ZSTD_compress(frame.data(), frame.size(), text.data(), text.size(), z::ZSTD_CLEVEL_DEFAULT);
    std::println("{} -> {} bytes", text.size(), ZSTD_isError(n) ? 0 : n);
}
```

## Scope and macros

The module exports the stable API. The experimental section of `<zstd.h>`
(behind `ZSTD_STATIC_LINKING_ONLY`) may change between releases and is not
exported. `<zdict.h>` is not exported either: `compat.zstd` does not build
the dictionary builder. Raw-content dictionaries work through `ZSTD_createCDict`
and `ZSTD_createDDict`.

A named module cannot export a macro. The constants are `inline constexpr`
of the same names in `mcpplibs::mwrap::zstd::macros`. `ZSTD_COMPRESSBOUND`
takes an argument and stays a macro in `<mwrap/zstd/macros.hpp>`; it names
`size_t`, so the unit imports `std.compat`. The visibility and deprecation
macros only spell the declarations. A macro expands even in a qualified name. A
unit that includes `<zstd.h>` beside the module reads the constants through the
header's macros ([docs/usage.md](docs/usage.md)).

## Build and testing

Linux, macOS and Windows CI build the modules with GCC and LLVM and run the
tests: a one-shot round trip, a level-19 frame with a checksum that detects
damage, a stream fed in pieces, a raw-content dictionary, the error code of
garbage input, the version and the bound against their macros, every constant
against its macro, and header mixing. CI also runs:

- the export audit ([tools/generate.py](tools/generate.py) `--check`): the
  module, the macro mapping, the macro header and the constant test are
  regenerated from the headers as clang reads them and compared, and on macOS
  and Windows every name the headers declare there is exported;
- four of upstream's examples over the same library
  ([tools/run_conformance.py](tools/run_conformance.py)).

A separate job scaffolds the default template as an installed package and runs
it.

## License

[Apache-2.0](LICENSE) for the wrapper, by mcpp-community ([NOTICE](NOTICE)).
Zstandard remains under the BSD license or the GPLv2
([upstream/zstd/LICENSE](upstream/zstd/LICENSE),
[COPYING](upstream/zstd/COPYING), [README](upstream/zstd/README.md)).
