// The header and the module in one translation unit: the same entities, so a
// context created through one spelling is freed through the other.
#include <zstd.h>
import std;
import mcpplibs.mwrap.zstd;

int main()
{
    ZSTD_CCtx* c = ::ZSTD_createCCtx();                          // the header's declaration
    const bool set = !ZSTD_isError(ZSTD_CCtx_setParameter(c, ZSTD_c_compressionLevel, ZSTD_CLEVEL_DEFAULT));
    const bool freed = ZSTD_freeCCtx(c) == 0;                    // the module's
    const bool same = &::ZSTD_compress == &ZSTD_compress;
    std::println("{}", set && freed && same ? "header and module agree" : "FAIL");
    return set && freed && same ? 0 : 1;
}
