// The module's functions over compat.zstd: a one-shot round trip, a frame
// with a checksum through the advanced parameters, a stream, a raw-content
// dictionary, an error code, and the version against its macros.
#include <mwrap/zstd/macros.hpp>
import std.compat;
import mcpplibs.mwrap.zstd;

namespace m = mcpplibs::mwrap::zstd::macros;

int main()
{
    int failures = 0;
    auto check = [&](bool ok, std::string_view what) {
        std::println("{} {}", ok ? "ok  " : "FAIL", what);
        failures += ok ? 0 : 1;
    };

    std::string text;
    for (int i = 0; i < 2000; ++i) text += std::format("record {} of a repetitive log\n", i % 23);

    // One shot.
    std::string frame(ZSTD_compressBound(text.size()), '\0');
    const auto size = ZSTD_compress(frame.data(), frame.size(), text.data(), text.size(), m::ZSTD_CLEVEL_DEFAULT);
    check(!ZSTD_isError(size) && size < text.size() / 10, "ZSTD_compress shrinks the text");
    frame.resize(size);
    check(ZSTD_getFrameContentSize(frame.data(), frame.size()) == text.size(), "the frame states its content size");
    std::string back(text.size(), '\0');
    check(ZSTD_decompress(back.data(), back.size(), frame.data(), frame.size()) == text.size() && back == text,
          "ZSTD_decompress restores it");

    // The advanced parameters: a level and a checksum.
    ZSTD_CCtx* cctx = ZSTD_createCCtx();
    check(!ZSTD_isError(ZSTD_CCtx_setParameter(cctx, ZSTD_c_compressionLevel, 19))
              && !ZSTD_isError(ZSTD_CCtx_setParameter(cctx, ZSTD_c_checksumFlag, 1)), "ZSTD_CCtx_setParameter");
    std::string checked(ZSTD_compressBound(text.size()), '\0');
    const auto checked_size = ZSTD_compress2(cctx, checked.data(), checked.size(), text.data(), text.size());
    check(!ZSTD_isError(checked_size), "ZSTD_compress2 with a checksum");
    checked.resize(checked_size);
    checked[checked.size() - 1] ^= 1;  // the last byte is the checksum's
    const auto damaged = ZSTD_decompress(back.data(), back.size(), checked.data(), checked.size());
    check(ZSTD_isError(damaged) && ZSTD_getErrorCode(damaged) == ZSTD_error_checksum_wrong,
          "a damaged checksum is ZSTD_error_checksum_wrong");

    // A stream, fed in pieces and flushed at the end.
    check(!ZSTD_isError(ZSTD_CCtx_reset(cctx, ZSTD_reset_session_and_parameters)), "ZSTD_CCtx_reset");
    std::string streamed(ZSTD_compressBound(text.size()), '\0');
    ZSTD_outBuffer out{streamed.data(), streamed.size(), 0};
    for (std::size_t at = 0; at < text.size(); at += 4096) {
        const auto n = std::min<std::size_t>(4096, text.size() - at);
        ZSTD_inBuffer in{text.data() + at, n, 0};
        const bool last = at + n == text.size();
        std::size_t left;
        do left = ZSTD_compressStream2(cctx, &out, &in, last ? ZSTD_e_end : ZSTD_e_continue);
        while (!ZSTD_isError(left) && (last ? left != 0 : in.pos != in.size));
    }
    ZSTD_freeCCtx(cctx);
    ZSTD_DCtx* dctx = ZSTD_createDCtx();
    std::string unstreamed(text.size(), '\0');
    ZSTD_inBuffer in{streamed.data(), out.pos, 0};
    ZSTD_outBuffer whole{unstreamed.data(), unstreamed.size(), 0};
    const auto rest = ZSTD_decompressStream(dctx, &whole, &in);
    check(rest == 0 && whole.pos == text.size() && unstreamed == text, "ZSTD_decompressStream restores the stream");
    ZSTD_freeDCtx(dctx);

    // A raw-content dictionary: the second text compresses against the first.
    const std::string dictionary = text.substr(0, 4096);
    ZSTD_CDict* cdict = ZSTD_createCDict(dictionary.data(), dictionary.size(), 3);
    ZSTD_DDict* ddict = ZSTD_createDDict(dictionary.data(), dictionary.size());
    cctx = ZSTD_createCCtx();
    dctx = ZSTD_createDCtx();
    const std::string sample = text.substr(100, 600);
    std::string small(ZSTD_compressBound(sample.size()), '\0');
    const auto with = ZSTD_compress_usingCDict(cctx, small.data(), small.size(), sample.data(), sample.size(), cdict);
    const auto without = ZSTD_compress(frame.data(), frame.size(), sample.data(), sample.size(), 3);
    check(!ZSTD_isError(with) && with < without, "the dictionary helps");
    std::string sample_back(sample.size(), '\0');
    check(ZSTD_decompress_usingDDict(dctx, sample_back.data(), sample_back.size(), small.data(), with, ddict)
              == sample.size() && sample_back == sample, "ZSTD_decompress_usingDDict restores it");
    ZSTD_freeCCtx(cctx);
    ZSTD_freeDCtx(dctx);
    ZSTD_freeCDict(cdict);
    ZSTD_freeDDict(ddict);

    // Errors and the version.
    const auto garbage = ZSTD_decompress(back.data(), back.size(), "not a frame", 11);
    check(ZSTD_isError(garbage) && ZSTD_getErrorCode(garbage) == ZSTD_error_prefix_unknown,
          std::format("garbage is ZSTD_error_prefix_unknown ({})", ZSTD_getErrorName(garbage)));
    check(ZSTD_versionNumber() == m::ZSTD_VERSION_NUMBER && std::string_view(ZSTD_versionString()) == m::ZSTD_VERSION_STRING,
          "the library is the headers' version");
    check(ZSTD_COMPRESSBOUND(100000) == ZSTD_compressBound(100000), "ZSTD_COMPRESSBOUND is ZSTD_compressBound");
    std::println("{} failures", failures);
    return failures != 0;
}
