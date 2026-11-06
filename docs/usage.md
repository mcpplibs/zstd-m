# Usage and API

`mcpplibs.mwrap.zstd` 1.5.7 exports Zstandard's stable API, upstream's names
unchanged. This page lists what each module holds and the places where a module
and a header differ. [tools/generate.py](../tools/generate.py) writes the lists
from the headers, and CI checks them on every target.

## Modules

| Module | Holds |
|---|---|
| `mcpplibs.mwrap.zstd` | the stable API of `<zstd.h>`: one-shot `ZSTD_compress`, `ZSTD_decompress`, `ZSTD_compressBound`, `ZSTD_getFrameContentSize`, `ZSTD_findFrameCompressedSize`; explicit contexts (`ZSTD_CCtx`, `ZSTD_DCtx` and their `create`, `free`, `compressCCtx`, `decompressDCtx`); the advanced API (`ZSTD_cParameter`, `ZSTD_dParameter` and their enumerators, `ZSTD_CCtx_setParameter`, `ZSTD_compress2`, `ZSTD_cParam_getBounds`, `ZSTD_strategy`, `ZSTD_ResetDirective`); streaming (`ZSTD_inBuffer`, `ZSTD_outBuffer`, `ZSTD_EndDirective`, `ZSTD_compressStream2`, `ZSTD_decompressStream`, the `CStream`/`DStream` forms); dictionaries (`ZSTD_CDict`, `ZSTD_DDict`, `*_usingDict`, `*_usingCDict`, `*_usingDDict`, `ZSTD_CCtx_loadDictionary`, `refPrefix`, `getDictID_*`); `ZSTD_sizeof_*`; `ZSTD_versionNumber`, `ZSTD_versionString`, `ZSTD_isError`, `ZSTD_getErrorName`, levels. From `<zstd_errors.h>`: `ZSTD_ErrorCode` with every `ZSTD_error_*`, `ZSTD_getErrorCode`, `ZSTD_getErrorString`. Re-exports the macros module |
| `mcpplibs.mwrap.zstd.macros` | in `mcpplibs::mwrap::zstd::macros`: `ZSTD_VERSION_MAJOR`, `_MINOR`, `_RELEASE`, `_NUMBER`, `_STRING`; `ZSTD_CLEVEL_DEFAULT`; `ZSTD_MAGICNUMBER`, `ZSTD_MAGIC_DICTIONARY`, `ZSTD_MAGIC_SKIPPABLE_START`, `ZSTD_MAGIC_SKIPPABLE_MASK`; `ZSTD_BLOCKSIZELOG_MAX`, `ZSTD_BLOCKSIZE_MAX`; `ZSTD_CONTENTSIZE_UNKNOWN`, `ZSTD_CONTENTSIZE_ERROR`; `ZSTD_MAX_INPUT_SIZE` |

## What is not exported

- **The experimental API.** The part of `<zstd.h>` behind
  `ZSTD_STATIC_LINKING_ONLY` is declared only when a unit defines that macro
  before the header, and upstream may change it in any release. A program that
  needs it includes `<zstd.h>` with the macro and links the same
  `compat.zstd`.
- **`<zdict.h>`.** `compat.zstd` builds `lib/common`, `lib/compress` and
  `lib/decompress`, not `lib/dictBuilder`; the `ZDICT_*` functions would not
  link. A raw-content dictionary (any bytes) works with `ZSTD_createCDict`.

## Macros

- **Constants.** Each object-like macro whose expansion is a constant
  expression is an `inline constexpr` of the same name and value;
  tests/macros.cpp compares every one with its macro.
- **`ZSTD_COMPRESSBOUND(srcSize)`** is a constant expression where
  `ZSTD_compressBound` is a call, so it stays a macro in
  `<mwrap/zstd/macros.hpp>`, reading `ZSTD_MAX_INPUT_SIZE` from the macros
  module. It casts to `size_t`: import `std.compat`, which declares `::size_t`.
- **Declaration syntax.** `ZSTDLIB_API`, `ZSTDLIB_VISIBLE`, `ZSTDLIB_HIDDEN`,
  their `ZSTDERRORLIB_*` counterparts, `ZSTD_DEPRECATED`, and the
  stringification steps `ZSTD_QUOTE`, `ZSTD_EXPAND_AND_QUOTE`,
  `ZSTD_LIB_VERSION` (whose result is `ZSTD_VERSION_STRING`) are not offered.
  tools/surface.toml lists them.

## A header beside the module

`#include <zstd.h>` and `import mcpplibs.mwrap.zstd;` may appear in one unit:
they declare the same entities. A macro expands even inside a qualified name,
so `mcpplibs::mwrap::zstd::macros::ZSTD_CLEVEL_DEFAULT` written after the header
is `...::macros::3`. In such a unit use the header's macros, or read their values
under other names and `#undef` the macros before naming the constants
(tests/macros.cpp does this).

## Linking

The package depends on `compat.zstd` 1.5.7, which builds Zstandard from the
release sources with the target's toolchain, without assembly
(`ZSTD_DISABLE_ASM`). A program that imports the module links that library; it
does not look for a system zstd.
