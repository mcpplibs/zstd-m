#!/usr/bin/env python3
"""Write, or with --check audit, the parts of the wrapper that follow from the headers.

tools/surface.toml names the headers and classifies what the compiler cannot:
the configuration that consumers share with the compat package (`defines`,
defined before the headers), the macros that are how the headers are written
(`syntax`), the names that only some targets declare (`conditional`), and the
functions that the compat package does not build (`unbuilt`, not exported).
Everything else follows from the headers as the compiler reads them
(tools/api.py), with the include, define and target flags of the last
`mcpp build` (target/**/compile_commands.json):

  src/<name>.cppm                 every function, variable, type and enumerator,
                                  `export using ::name`
  src/macros.cppm                 every object-like macro that is a constant
                                  expression or a type, under its own name in
                                  mcpplibs::mwrap::<name>::macros
  include/mwrap/<name>/macros.hpp every other macro, upstream's definition
  tests/macros.cpp                each mapped constant and type against its macro
  tests/linked.cpp                the address of each exported function, so that
                                  the link proves the compat package defines it

The include guards and reserved identifiers (`__x`, `_X`) are recognised and
omitted. --check renders the same files in memory: on the host named by
`generated-on` they must be byte-identical; on every host, each name the
headers declare there must be exported, mapped, kept or classified, and each
unconditional export must be declared there.
The compiler is the clang of the build; run it after `mcpp build` with LLVM.
"""
import argparse
import json
from pathlib import Path
import re
import sys
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent))
import api  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
KEEP_JOINED = ('-I', '-isystem', '-idirafter', '-iquote', '-D', '-U', '--sysroot=', '-isysroot', '--target=',
               '-target', '-include', '-imsvc', '-fms-compatibility-version=', '-fms-runtime-lib=', '-fms-extensions')
KEEP_ALONE = ('-nostdinc++', '-nostdlibinc', '-nostdinc', '--no-default-config')
TAKES_VALUE = ('-I', '-isystem', '-idirafter', '-iquote', '-D', '-U', '-isysroot', '-target', '-include', '-imsvc')


def build_flags(name):
    """The clang of the newest LLVM build and its preprocessing and target flags for src/<name>.cppm."""
    databases = sorted((ROOT / 'target').glob('**/compile_commands.json'), key=lambda p: p.stat().st_mtime)
    for database in reversed(databases):
        for entry in json.loads(database.read_text(encoding='utf-8')):
            words = entry.get('arguments') or entry['command'].split()
            if Path(entry['file']).as_posix().endswith(f'src/{name}.cppm') and 'clang' in Path(words[0]).name:
                flags, rest = [], iter(words[1:])
                for word in rest:
                    if word in TAKES_VALUE:
                        flags += [word, next(rest)]
                    elif word in KEEP_ALONE or word.startswith(KEEP_JOINED):
                        flags.append(word)
                return words[0], flags
    sys.exit(f'no LLVM build of src/{name}.cppm; run `mcpp build --toolchain llvm@23.1.3` first')


def qualify(body, mapped, scope):
    return re.sub(r'(?<![\w:."])\b([A-Za-z_]\w*)\b',
                  lambda m: f'::{scope}::{m.group(1)}' if m.group(1) in mapped else m.group(1), body)


def classify(cfg, compiler, flags):
    flags = flags + [f'-D{d}' for d in cfg.get('defines', [])]
    headers = cfg['headers']
    owned = cfg.get('owned', headers)
    surface, macros = api.extract(compiler, flags, headers, owned)
    guards = api.guards(macros)
    # A reserved identifier (`__x`, `_X`) is the implementation's, never the library's API.
    reserved = {n for n in macros if re.match(r'_[_A-Z]', n)}
    syntax = set(cfg.get('syntax', [])) | reserved
    open_macros = {n: m for n, m in macros.items() if n not in guards and n not in syntax}
    constants = api.constant_macros(compiler, flags, headers, open_macros)
    types = api.type_macros(compiler, flags, headers, {n: m for n, m in open_macros.items() if n not in constants})
    kept = {n: m for n, m in open_macros.items() if n not in constants and n not in types}
    return surface, macros, guards, constants, types, kept


def render(cfg, surface, constants, types, kept):
    name = cfg['name']
    scope = f'mcpplibs::mwrap::{name}'
    conditional = cfg.get('conditional', {})
    # The configuration the compat package compiles with and its consumers must share.
    includes = '\n'.join([f'#ifndef {d}\n#define {d}\n#endif' for d in cfg.get('defines', [])]
                         + [f'#include <{h}>' for h in cfg['headers']])
    declared = surface['functions'] | surface['variables'] | surface['types'] | surface['enumerators']
    exported = sorted(declared - set(conditional) - set(cfg.get('unbuilt', [])))
    cap = f'mwrap_{name}_capture'

    module = [f"// mcpplibs.mwrap.{name} --- {cfg['title']} as a C++ module. Every exported name is",
              "// the upstream entity of the headers below, unchanged, in the global namespace where",
              f"// upstream declares it; the root also re-exports the macro mapping. The implementation",
              f"// is compat.{cfg['compat']} {cfg['version']}. Written by tools/generate.py from the headers.",
              'module;', includes, '', f'export module mcpplibs.mwrap.{name};', '',
              f'export import mcpplibs.mwrap.{name}.macros;', '', 'export {']
    module += [f'using ::{n};' for n in exported]
    module.append('}')
    for condition in sorted(set(conditional.values())):
        module += ['', f'#if {condition}', 'export {']
        module += [f'using ::{n};' for n in sorted(conditional) if conditional[n] == condition]
        module += ['}', '#endif']

    mapped = sorted(constants | types)
    macros = [f"// mcpplibs.mwrap.{name}.macros --- the macros of the headers that are a constant or a",
              "// type, under their original names in " + scope + "::macros, each equal to",
              "// the macro where the module is built (a named module cannot export a macro). The",
              f"// other macros are in <mwrap/{name}/macros.hpp>. Written by tools/generate.py.",
              'module;', includes, '', '// The values, taken under other names while the macros are defined.',
              f'namespace {cap} {{']
    macros += [f'inline constexpr auto value_{n} = ({n});' if n in constants else f'using type_{n} = {n};'
               for n in mapped]
    macros += ['}'] + [f'#undef {n}' for n in mapped]
    macros += ['', f'export module mcpplibs.mwrap.{name}.macros;', '', f'export namespace {scope}::macros {{']
    macros += [f'inline constexpr auto {n} = {cap}::value_{n};' if n in constants else f'using {n} = {cap}::type_{n};'
               for n in mapped]
    macros.append('}')

    guard = f'MWRAP_{name.upper()}_MACROS_HPP'
    header = [f'// <mwrap/{name}/macros.hpp> --- the macros of the headers that are neither a constant',
              '// nor a type: they take arguments, or call a function. A named module cannot export a',
              f'// macro: include this header before `import mcpplibs.mwrap.{name};`. Each definition is',
              f"// upstream's ({cfg['title']}, {cfg['license']}), made only where the upstream header has",
              f'// not defined it, with the constants it names read from {scope}::macros',
              '// and NULL written nullptr.',
              '// The upstream header included after this one redefines these macros.',
              '// Written by tools/generate.py.',
              f'#ifndef {guard}', f'#define {guard}']
    for n in sorted(kept):
        # A module-only unit has no NULL macro; in C++ nullptr is its meaning.
        body = re.sub(r'\bNULL\b', 'nullptr', qualify(kept[n]['body'], set(mapped), f'{scope}::macros'))
        header += ['', f'#ifndef {n}', f"#define {n}{kept[n]['params'] or ''} {body}".rstrip(), '#endif']
    if not kept:
        header += ['', '// The headers of this release define no such macro.']
    header += ['', f'#endif  // {guard}']

    test = [f'// Each constant and type of mcpplibs.mwrap.{name}.macros equals its macro. A macro',
            '// expands even in a qualified name, so the values of the headers are taken under other',
            '// names and the macros undefined before the mapped names are used. Written by',
            '// tools/generate.py.', includes, '', 'namespace header {']
    test += [f'inline constexpr auto value_{n} = ({n});' if n in constants else f'using type_{n} = {n};' for n in mapped]
    test += ['}'] + [f'#undef {n}' for n in mapped]
    test += ['', 'import std;', f'import mcpplibs.mwrap.{name}.macros;', '',
             f'namespace m = {scope}::macros;', '']
    test += [f'static_assert(std::is_same_v<m::{n}, header::type_{n}>, "{n}");' for n in sorted(types)]
    test += ['', 'template <class A, class B>', 'bool same(A a, B b)', '{',
             '    if constexpr (std::is_convertible_v<A, const char*> && std::is_convertible_v<B, const char*>)',
             '        return std::string_view(a) == std::string_view(b);',
             '    else',
             '        return a == b;',
             '}', '', 'int main()', '{', '    int differ = 0;']
    test += [f'    if (!same(m::{n}, header::value_{n})) {{ std::println("FAIL {n}"); ++differ; }}' for n in sorted(constants)]
    test += [f'    std::println("{len(constants)} constants and {len(types)} types compared, {{}} differ", differ);',
             '    return differ != 0;', '}']
    functions = sorted(surface['functions'] - set(conditional) - set(cfg.get('unbuilt', [])))
    linked = [f'// Every function that mcpplibs.mwrap.{name} exports, by address: the program links only',
              f'// where compat.{cfg["compat"]} defines each one. Written by tools/generate.py.',
              'import std;', f'import mcpplibs.mwrap.{name};', '', 'int main()', '{',
              '    // volatile: an optimiser may not drop a reference, so each one reaches the link.',
              '    const void* volatile functions[] = {']
    linked += [f'        reinterpret_cast<const void*>(&{n}),' for n in functions]
    linked += ['    };', '    int missing = 0;', '    for (const void* f : functions) missing += f == nullptr;',
               f'    std::println("{len(functions)} functions linked, {{}} null", missing);',
               '    return missing != 0;', '}']
    join = lambda lines: '\n'.join(lines) + '\n'
    return {f'src/{name}.cppm': join(module), 'src/macros.cppm': join(macros),
            f'include/mwrap/{name}/macros.hpp': join(header), 'tests/macros.cpp': join(test),
            'tests/linked.cpp': join(linked)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='audit instead of writing')
    args = parser.parse_args()
    cfg = tomllib.loads((ROOT / 'tools/surface.toml').read_text(encoding='utf-8'))
    compiler, flags = build_flags(cfg['name'])
    surface, macros, guards, constants, types, kept = classify(cfg, compiler, flags)
    files = render(cfg, surface, constants, types, kept)
    problems = []
    host = {'linux': 'linux', 'darwin': 'macos', 'win32': 'windows'}.get(sys.platform, sys.platform)
    if not args.check:
        for path, text in files.items():
            target = ROOT / path
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or target.read_text(encoding='utf-8') != text:
                target.write_text(text, encoding='utf-8', newline='\n')
    elif host == cfg['generated-on']:
        problems += [f'differs from the headers: {p}' for p, t in files.items()
                     if not (ROOT / p).exists() or (ROOT / p).read_text(encoding='utf-8') != t]
    else:
        # Another host: its declarations against the files written on `generated-on`.
        module = (ROOT / f"src/{cfg['name']}.cppm").read_text(encoding='utf-8')
        written = set(re.findall(r'using ::(\w+);', module))
        unconditional = set(re.findall(r'using ::(\w+);', module.split('\n#if ')[0]))
        declared = surface['functions'] | surface['variables'] | surface['types'] | surface['enumerators']
        mapping = (ROOT / 'src/macros.cppm').read_text(encoding='utf-8')
        mapped = set(re.findall(r'^#undef (\w+)$', mapping, flags=re.M))
        kept_written = set(re.findall(r'^#ifndef (\w+)$', (ROOT / f"include/mwrap/{cfg['name']}/macros.hpp")
                                      .read_text(encoding='utf-8'), flags=re.M))
        problems += [f'declared here, not exported: {n}' for n in sorted(declared - written - set(cfg.get('unbuilt', [])))]
        problems += [f'exported, not declared here: {n}' for n in sorted(unconditional - declared)]
        problems += [f'macro here, neither mapped, kept nor classified: {n}' for n in sorted(
            set(macros) - guards - set(cfg.get('syntax', [])) - mapped - kept_written)
            if not re.match(r'_[_A-Z]', n)]
        problems += [f'mapped, not a constant or type here: {n}' for n in sorted(mapped - constants - types)]
    problems += [f'internal linkage, cannot be exported: {n}' for n in sorted(surface['internal'])
                 if n not in cfg.get('adapted', [])]
    for problem in problems:
        print(problem)
    print(f"{host}: {len(surface['functions'])} functions, {len(surface['variables'])} variables, "
          f"{len(surface['types'])} types, {len(surface['enumerators'])} enumerators; {len(constants)} constant and "
          f"{len(types)} type macros mapped, {len(kept)} kept, {len(guards)} guards, "
          f"{len(set(cfg.get('syntax', [])) & set(macros))} syntax; {len(problems)} problems")
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
