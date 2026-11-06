// mcpplibs.mwrap.zstd.macros --- the macros of the headers that are a constant or a
// type, under their original names in mcpplibs::mwrap::zstd::macros, each equal to
// the macro where the module is built (a named module cannot export a macro). The
// other macros are in <mwrap/zstd/macros.hpp>. Written by tools/generate.py.
module;
#include <zstd.h>
#include <zstd_errors.h>

// The values, taken under other names while the macros are defined.
namespace mwrap_zstd_capture {
inline constexpr auto value_ZSTD_BLOCKSIZELOG_MAX = (ZSTD_BLOCKSIZELOG_MAX);
inline constexpr auto value_ZSTD_BLOCKSIZE_MAX = (ZSTD_BLOCKSIZE_MAX);
inline constexpr auto value_ZSTD_CLEVEL_DEFAULT = (ZSTD_CLEVEL_DEFAULT);
inline constexpr auto value_ZSTD_CONTENTSIZE_ERROR = (ZSTD_CONTENTSIZE_ERROR);
inline constexpr auto value_ZSTD_CONTENTSIZE_UNKNOWN = (ZSTD_CONTENTSIZE_UNKNOWN);
inline constexpr auto value_ZSTD_MAGICNUMBER = (ZSTD_MAGICNUMBER);
inline constexpr auto value_ZSTD_MAGIC_DICTIONARY = (ZSTD_MAGIC_DICTIONARY);
inline constexpr auto value_ZSTD_MAGIC_SKIPPABLE_MASK = (ZSTD_MAGIC_SKIPPABLE_MASK);
inline constexpr auto value_ZSTD_MAGIC_SKIPPABLE_START = (ZSTD_MAGIC_SKIPPABLE_START);
inline constexpr auto value_ZSTD_MAX_INPUT_SIZE = (ZSTD_MAX_INPUT_SIZE);
inline constexpr auto value_ZSTD_VERSION_MAJOR = (ZSTD_VERSION_MAJOR);
inline constexpr auto value_ZSTD_VERSION_MINOR = (ZSTD_VERSION_MINOR);
inline constexpr auto value_ZSTD_VERSION_NUMBER = (ZSTD_VERSION_NUMBER);
inline constexpr auto value_ZSTD_VERSION_RELEASE = (ZSTD_VERSION_RELEASE);
inline constexpr auto value_ZSTD_VERSION_STRING = (ZSTD_VERSION_STRING);
}
#undef ZSTD_BLOCKSIZELOG_MAX
#undef ZSTD_BLOCKSIZE_MAX
#undef ZSTD_CLEVEL_DEFAULT
#undef ZSTD_CONTENTSIZE_ERROR
#undef ZSTD_CONTENTSIZE_UNKNOWN
#undef ZSTD_MAGICNUMBER
#undef ZSTD_MAGIC_DICTIONARY
#undef ZSTD_MAGIC_SKIPPABLE_MASK
#undef ZSTD_MAGIC_SKIPPABLE_START
#undef ZSTD_MAX_INPUT_SIZE
#undef ZSTD_VERSION_MAJOR
#undef ZSTD_VERSION_MINOR
#undef ZSTD_VERSION_NUMBER
#undef ZSTD_VERSION_RELEASE
#undef ZSTD_VERSION_STRING

export module mcpplibs.mwrap.zstd.macros;

export namespace mcpplibs::mwrap::zstd::macros {
inline constexpr auto ZSTD_BLOCKSIZELOG_MAX = mwrap_zstd_capture::value_ZSTD_BLOCKSIZELOG_MAX;
inline constexpr auto ZSTD_BLOCKSIZE_MAX = mwrap_zstd_capture::value_ZSTD_BLOCKSIZE_MAX;
inline constexpr auto ZSTD_CLEVEL_DEFAULT = mwrap_zstd_capture::value_ZSTD_CLEVEL_DEFAULT;
inline constexpr auto ZSTD_CONTENTSIZE_ERROR = mwrap_zstd_capture::value_ZSTD_CONTENTSIZE_ERROR;
inline constexpr auto ZSTD_CONTENTSIZE_UNKNOWN = mwrap_zstd_capture::value_ZSTD_CONTENTSIZE_UNKNOWN;
inline constexpr auto ZSTD_MAGICNUMBER = mwrap_zstd_capture::value_ZSTD_MAGICNUMBER;
inline constexpr auto ZSTD_MAGIC_DICTIONARY = mwrap_zstd_capture::value_ZSTD_MAGIC_DICTIONARY;
inline constexpr auto ZSTD_MAGIC_SKIPPABLE_MASK = mwrap_zstd_capture::value_ZSTD_MAGIC_SKIPPABLE_MASK;
inline constexpr auto ZSTD_MAGIC_SKIPPABLE_START = mwrap_zstd_capture::value_ZSTD_MAGIC_SKIPPABLE_START;
inline constexpr auto ZSTD_MAX_INPUT_SIZE = mwrap_zstd_capture::value_ZSTD_MAX_INPUT_SIZE;
inline constexpr auto ZSTD_VERSION_MAJOR = mwrap_zstd_capture::value_ZSTD_VERSION_MAJOR;
inline constexpr auto ZSTD_VERSION_MINOR = mwrap_zstd_capture::value_ZSTD_VERSION_MINOR;
inline constexpr auto ZSTD_VERSION_NUMBER = mwrap_zstd_capture::value_ZSTD_VERSION_NUMBER;
inline constexpr auto ZSTD_VERSION_RELEASE = mwrap_zstd_capture::value_ZSTD_VERSION_RELEASE;
inline constexpr auto ZSTD_VERSION_STRING = mwrap_zstd_capture::value_ZSTD_VERSION_STRING;
}
