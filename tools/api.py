#!/usr/bin/env python3
"""The public API of a set of C headers, as the compiler reads them.

`extract` returns the functions, variables, types and enumerators that the
owned headers declare, and the macros that they define, as the compiler's AST and
preprocessor see them in a C++23 translation unit including the headers.
`constant_macros` and `type_macros` select the object-like macros whose
expansion is a constant expression or a type. tools/generate.py writes the
module from these sets and audits it against them.
"""
import json
from pathlib import Path
import re
import subprocess


def _run(cmd, stdin):
    return subprocess.run(cmd, input=stdin, capture_output=True, text=True, check=True).stdout


def _owned(path, owned):
    path = path.replace('\\', '/')
    return any(path == name or path.endswith('/' + name) for name in owned)


def extract(compiler, flags, headers, owned=None):
    """`flags`: the compiler's include, define and target flags for the module;
    `owned`: the header files whose declarations are the API (default: `headers`)."""
    owned = list(owned or headers)
    source = ''.join(f'#include <{h}>\n' for h in headers)
    flags = ['-x', 'c++', '-std=c++23', *flags]
    ast = json.loads(_run([compiler, *flags, '-fsyntax-only', '-Xclang', '-ast-dump=json', '-'], source))
    api = {'functions': set(), 'internal': set(), 'variables': set(), 'types': set(), 'enumerators': set()}
    current = ['']

    def mine(node):
        # The AST names a file only where it changes from the previous node.
        loc = node.get('loc', {})
        for where in (loc, loc.get('spellingLoc', {}), loc.get('expansionLoc', {})):
            if 'file' in where:
                current[0] = where['file']
        return _owned(current[0], owned)

    def walk(nodes):
        for node in nodes:
            kind = node.get('kind')
            if kind == 'LinkageSpecDecl':
                mine(node)
                walk(node.get('inner', []))
                continue
            if not mine(node) or node.get('isImplicit'):
                continue
            name = node.get('name')
            if kind == 'EnumDecl':
                api['enumerators'] |= {e['name'] for e in node.get('inner', []) if e.get('kind') == 'EnumConstantDecl'}
            if not name:
                continue
            if kind == 'FunctionDecl':
                api['internal' if node.get('storageClass') == 'static' else 'functions'].add(name)
            elif kind == 'VarDecl' and node.get('storageClass') == 'extern':
                api['variables'].add(name)
            elif kind in ('TypedefDecl', 'TypeAliasDecl', 'RecordDecl', 'CXXRecordDecl', 'EnumDecl'):
                api['types'].add(name)
    walk(ast.get('inner', []))
    api['functions'] -= api['internal']

    macros = {}
    current = ''
    for line in _run([compiler, *flags, '-E', '-dD', '-'], source).splitlines():
        marker = re.match(r'#\s*(?:line\s+)?\d+\s+"([^"]*)"', line)
        if marker:
            current = marker.group(1)
            continue
        define = re.match(r'#define\s+([A-Za-z_][A-Za-z_0-9]*)(\([^)]*\))?\s*(.*)$', line)
        if define and _owned(current, owned):
            macros[define.group(1)] = {'params': define.group(2), 'body': define.group(3).strip(), 'file': current}
        undefine = re.match(r'#undef\s+([A-Za-z_][A-Za-z_0-9]*)', line)
        if undefine:
            macros.pop(undefine.group(1), None)
    return api, macros


def guards(macros):
    """The include guards among `macros`. An empty macro that the first
    conditional directive of its file tests (`#ifndef G` or `#if !defined(G)`),
    or a macro named like a guard (`..._H`, `..._H_<suffix>`, `..._INCLUDED`)
    that its file defines right after `#ifndef G`."""
    found = set()
    for name, macro in macros.items():
        if macro['params'] is not None:
            continue
        try:
            text = Path(macro['file']).read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        text = re.sub(r'/\*.*?\*/', ' ', text, flags=re.S)
        first = re.search(r'^\s*#\s*if.*$', text, flags=re.M)
        tested_first = first and re.fullmatch(
            r'\s*#\s*(?:ifndef\s+' + name + r'|if\s+!\s*defined\s*\(?\s*' + name + r'\s*\)?)\s*', first.group(0))
        named = re.search(r'_H(?:_\w+)?$|_INCLUDED$', name) and re.search(
            r'^\s*#\s*ifndef\s+' + name + r'\s*\n\s*#\s*define\s+' + name + r'\b', text, flags=re.M)
        if (tested_first and not macro['body']) or named:
            found.add(name)
    return found


def _accepted(compiler, flags, headers, names, form):
    """The names for which `form` (with {i} and {n}) compiles after the headers:
    one translation unit, dropping the lines with an error until none remain."""
    head = ''.join(f'#include <{h}>\n' for h in headers)
    pending = sorted(names)
    while pending:
        probe = head + '#line 1 "mwrap-probe"\n' + ''.join(form.format(i=i, n=n) + '\n' for i, n in enumerate(pending))
        result = subprocess.run([compiler, '-x', 'c++', '-std=c++23', *flags, '-fsyntax-only', '-ferror-limit=0', '-'],
                                input=probe, capture_output=True, text=True)
        if result.returncode == 0:
            return set(pending)
        bad = {int(m.group(1)) - 1 for m in re.finditer(r'mwrap-probe:(\d+):\d+: error', result.stderr)}
        if not bad:
            raise RuntimeError(result.stderr[-2000:])
        pending = [n for i, n in enumerate(pending) if i not in bad]
    return set()


def constant_macros(compiler, flags, headers, macros):
    """The object-like macros among `macros` whose expansion is a constant expression."""
    names = [n for n, m in macros.items() if m['params'] is None and m['body']]
    return _accepted(compiler, flags, headers, names, 'inline constexpr auto mwrap_probe_{i} = ({n});')


def type_macros(compiler, flags, headers, macros):
    """The object-like macros among `macros` whose expansion is a type."""
    names = [n for n, m in macros.items() if m['params'] is None and m['body']]
    return _accepted(compiler, flags, headers, names, 'using mwrap_probe_{i} = {n};')
