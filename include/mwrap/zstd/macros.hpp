// <mwrap/zstd/macros.hpp> --- the macros of the headers that are neither a constant
// nor a type: they take arguments, or call a function. A named module cannot export a
// macro: include this header before `import mcpplibs.mwrap.zstd;`. Each definition is
// upstream's (Zstandard 1.5.7, BSD license or GPLv2), made only where the upstream header has
// not defined it, with the constants it names read from mcpplibs::mwrap::zstd::macros.
// The upstream header included after this one redefines these macros.
// Written by tools/generate.py.
#ifndef MWRAP_ZSTD_MACROS_HPP
#define MWRAP_ZSTD_MACROS_HPP

#ifndef ZSTD_COMPRESSBOUND
#define ZSTD_COMPRESSBOUND(srcSize) (((size_t)(srcSize) >= ::mcpplibs::mwrap::zstd::macros::ZSTD_MAX_INPUT_SIZE) ? 0 : (srcSize) + ((srcSize)>>8) + (((srcSize) < (128<<10)) ? (((128<<10) - (srcSize)) >> 11) : 0))
#endif

#endif  // MWRAP_ZSTD_MACROS_HPP
