// Each constant and type of mcpplibs.mwrap.zstd.macros equals its macro. A macro
// expands even in a qualified name, so the values of the headers are taken under other
// names and the macros undefined before the mapped names are used. Written by
// tools/generate.py.
#include <zstd.h>
#include <zstd_errors.h>

namespace header {
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

import std;
import mcpplibs.mwrap.zstd.macros;

namespace m = mcpplibs::mwrap::zstd::macros;


template <class A, class B>
bool same(A a, B b)
{
    if constexpr (std::is_convertible_v<A, const char*> && std::is_convertible_v<B, const char*>)
        return std::string_view(a) == std::string_view(b);
    else
        return a == b;
}

int main()
{
    int differ = 0;
    if (!same(m::ZSTD_BLOCKSIZELOG_MAX, header::value_ZSTD_BLOCKSIZELOG_MAX)) { std::println("FAIL ZSTD_BLOCKSIZELOG_MAX"); ++differ; }
    if (!same(m::ZSTD_BLOCKSIZE_MAX, header::value_ZSTD_BLOCKSIZE_MAX)) { std::println("FAIL ZSTD_BLOCKSIZE_MAX"); ++differ; }
    if (!same(m::ZSTD_CLEVEL_DEFAULT, header::value_ZSTD_CLEVEL_DEFAULT)) { std::println("FAIL ZSTD_CLEVEL_DEFAULT"); ++differ; }
    if (!same(m::ZSTD_CONTENTSIZE_ERROR, header::value_ZSTD_CONTENTSIZE_ERROR)) { std::println("FAIL ZSTD_CONTENTSIZE_ERROR"); ++differ; }
    if (!same(m::ZSTD_CONTENTSIZE_UNKNOWN, header::value_ZSTD_CONTENTSIZE_UNKNOWN)) { std::println("FAIL ZSTD_CONTENTSIZE_UNKNOWN"); ++differ; }
    if (!same(m::ZSTD_MAGICNUMBER, header::value_ZSTD_MAGICNUMBER)) { std::println("FAIL ZSTD_MAGICNUMBER"); ++differ; }
    if (!same(m::ZSTD_MAGIC_DICTIONARY, header::value_ZSTD_MAGIC_DICTIONARY)) { std::println("FAIL ZSTD_MAGIC_DICTIONARY"); ++differ; }
    if (!same(m::ZSTD_MAGIC_SKIPPABLE_MASK, header::value_ZSTD_MAGIC_SKIPPABLE_MASK)) { std::println("FAIL ZSTD_MAGIC_SKIPPABLE_MASK"); ++differ; }
    if (!same(m::ZSTD_MAGIC_SKIPPABLE_START, header::value_ZSTD_MAGIC_SKIPPABLE_START)) { std::println("FAIL ZSTD_MAGIC_SKIPPABLE_START"); ++differ; }
    if (!same(m::ZSTD_MAX_INPUT_SIZE, header::value_ZSTD_MAX_INPUT_SIZE)) { std::println("FAIL ZSTD_MAX_INPUT_SIZE"); ++differ; }
    if (!same(m::ZSTD_VERSION_MAJOR, header::value_ZSTD_VERSION_MAJOR)) { std::println("FAIL ZSTD_VERSION_MAJOR"); ++differ; }
    if (!same(m::ZSTD_VERSION_MINOR, header::value_ZSTD_VERSION_MINOR)) { std::println("FAIL ZSTD_VERSION_MINOR"); ++differ; }
    if (!same(m::ZSTD_VERSION_NUMBER, header::value_ZSTD_VERSION_NUMBER)) { std::println("FAIL ZSTD_VERSION_NUMBER"); ++differ; }
    if (!same(m::ZSTD_VERSION_RELEASE, header::value_ZSTD_VERSION_RELEASE)) { std::println("FAIL ZSTD_VERSION_RELEASE"); ++differ; }
    if (!same(m::ZSTD_VERSION_STRING, header::value_ZSTD_VERSION_STRING)) { std::println("FAIL ZSTD_VERSION_STRING"); ++differ; }
    std::println("15 constants and 0 types compared, {} differ", differ);
    return differ != 0;
}
