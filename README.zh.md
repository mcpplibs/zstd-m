# zstd

> Zstandard——快速无损压缩库，以 C++23 模块提供。

[English](README.md) · **简体中文** · [上游](https://github.com/facebook/zstd) · [发布](https://github.com/mcpplibs/zstd-m/releases) · [mcpp](https://github.com/mcpp-community/mcpp) · [索引](https://github.com/mcpplibs/mcpp-index)

[![C++23](https://img.shields.io/badge/C%2B%2B-23-blue.svg)](https://en.cppreference.com/w/cpp/23)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![mcpp-community](https://img.shields.io/badge/mcpp--community-mwrap-blue)](https://github.com/mcpp-community)
[![CI](https://github.com/mcpplibs/zstd-m/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mcpplibs/zstd-m/actions/workflows/ci.yml)

上游 API 不变：`ZSTD_compress`、`ZSTD_compress2`、`ZSTD_decompressStream`、`ZSTD_CCtx`、`ZSTD_cParameter` 及其枚举值、
`<zstd_errors.h>` 的错误码都是上游实体，位于上游声明它们的全局命名空间。库本身是 `compat.zstd` 1.5.7；常量宏映射为
C++ 常量。每次 CI 都在同一份库上运行上游自己的示例并完成往返。

## 模块

- `import mcpplibs.mwrap.zstd;`：`<zstd.h>` 的稳定 API 与 `<zstd_errors.h>` 的错误码，并重新导出宏模块
- `import mcpplibs.mwrap.zstd.macros;`：`ZSTD_CLEVEL_DEFAULT`、`ZSTD_CONTENTSIZE_ERROR`、`ZSTD_MAGICNUMBER`、`ZSTD_VERSION_NUMBER` 等，位于 `mcpplibs::mwrap::zstd::macros`
- `#include <mwrap/zstd/macros.hpp>`：`ZSTD_COMPRESSBOUND(size)`，以常量表达式给出上界

> 更多模块 API -> [用法与 API](docs/usage.md)

## 快速开始

```sh
mcpp new squeeze --template mcpplibs.mwrap.zstd@1.5.7
cd squeeze
mcpp run
```

默认模板以两个级别带校验和压缩一段文本，再还原并打印大小。

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

## 范围与宏

模块导出稳定 API。`<zstd.h>` 的实验部分（`ZSTD_STATIC_LINKING_ONLY` 之后）可能在版本之间变化，不导出。`<zdict.h>`
也不导出：`compat.zstd` 不构建字典训练器。原始内容字典可经 `ZSTD_createCDict` 与 `ZSTD_createDDict` 使用。

命名模块不能导出宏。常量映射为 `mcpplibs::mwrap::zstd::macros` 中同名的 `inline constexpr`。`ZSTD_COMPRESSBOUND`
带参数，保留为 `<mwrap/zstd/macros.hpp>` 中的宏；它用到 `size_t`，所以该翻译单元导入 `std.compat`。可见性与弃用宏只用于
书写声明。宏在限定名中也会展开。同时包含 `<zstd.h>` 的翻译单元经头文件的宏读取常量（[docs/usage.md](docs/usage.md)）。

## 构建与测试

Linux、macOS、Windows 的 CI 用 GCC 与 LLVM 构建模块并运行测试：一次调用的往返、带校验和的 19 级帧及其损坏检测、分段
输入的流、原始内容字典、无效输入的错误码、版本与上界同其宏相等、每个常量同其宏相等、每个导出函数都能链接、头文件混用。CI 还运行：

- 导出审计（[tools/generate.py](tools/generate.py) `--check`）：按 clang 读到的头文件重新生成模块、宏映射、宏头文件与
  生成的测试并逐字节比较；在 macOS 与 Windows 上检查头文件在该平台声明的每个名字都已导出；
- 在同一份库上运行上游的四个示例（[tools/run_conformance.py](tools/run_conformance.py)）。

另一个作业把默认模板当作已安装的包生成项目并运行。

## 许可

包装部分为 [Apache-2.0](LICENSE)，作者 mcpp-community（[NOTICE](NOTICE)）。Zstandard 仍遵循 BSD 许可或 GPLv2
（[upstream/zstd/LICENSE](upstream/zstd/LICENSE)、[COPYING](upstream/zstd/COPYING)、[README](upstream/zstd/README.md)）。
