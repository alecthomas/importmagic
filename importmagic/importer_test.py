from __future__ import absolute_import

from textwrap import dedent

from importmagic.importer import update_imports
from importmagic.symbols import Scope


def test_deep_import_of_unknown_symbol(index):
    src = dedent("""
        print(os.unknown('/'))
         """).strip()
    unresolved, unreferenced = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['os.unknown'])
    new_src = update_imports(src, index, unresolved, unreferenced)
    assert dedent("""
        import os


        print(os.unknown('/'))
        """).strip() == new_src


def test_import_future_preserved(index):
    src = 'from __future__ import absolute_import'
    unresolved, unreferenced = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert not unresolved
    assert not unreferenced
    new_src = update_imports(src, index, unresolved, unreferenced).strip()
    assert src == new_src


def test_update_imports_inserts_initial_imports(index):
    src = dedent("""
        print(os.path.basename('sys/foo'))
        print(sys.path[0])
        print(basename('sys/foo'))
        print(path.basename('sys/foo'))
        """).strip()
    unresolved, unreferenced = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['os.path.basename', 'sys.path', 'basename', 'path.basename'])
    new_src = update_imports(src, index, unresolved, unreferenced)
    assert dedent("""
        import os.path
        import sys
        from os import path
        from os.path import basename


        print(os.path.basename('sys/foo'))
        print(sys.path[0])
        print(basename('sys/foo'))
        print(path.basename('sys/foo'))
        """).strip() == new_src


def test_update_imports_inserts_imports(index):
    src = dedent("""
        import sys

        print(os.path.basename("sys/foo"))
        print(sys.path[0])
        """).strip()
    unresolved, unreferenced = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['os.path.basename'])
    new_src = update_imports(src, index, unresolved, unreferenced)
    assert dedent("""
        import os.path
        import sys


        print(os.path.basename("sys/foo"))
        print(sys.path[0])
        """).strip() == new_src


def test_update_imports_correctly_aliases(index):
    src = dedent('''
        print(basename('src/foo'))
        ''').strip()
    unresolved, unreferenced = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['basename'])
    new_src = update_imports(src, index, unresolved, unreferenced)
    assert dedent('''
        from os.path import basename


        print(basename('src/foo'))
        ''').strip() == new_src


def test_parse_imports(index):
    src = dedent('''
        import os, sys as sys
        import sys as sys
        from os.path import basename

        from os import (
            path,
            posixpath
            )

        def main():
            pass
        ''').strip()
    unresolved, unreferenced = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    new_src = update_imports(src, index, unresolved, unreferenced)
    assert dedent(r'''
        def main():
            pass
        ''').strip() == new_src


def test_imports_inserted_after_preamble(index):
    src = dedent('''
        # Comment

        """Docstring"""

        def func(n):
            print(basename(n))
        ''').strip()
    unresolved, unreferenced = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    new_src = update_imports(src, index, unresolved, unreferenced)
    assert dedent('''
        # Comment

        """Docstring"""

        from os.path import basename


        def func(n):
            print(basename(n))
        ''').strip() == new_src


def test_imports_dont_delete_trailing_comments(index):
    src = dedent('''
        import sys

        # Some function
        def func(n):
            print(basename(n))
        ''').strip()
    scope = Scope.from_source(src)
    new_src = update_imports(src, index, *scope.find_unresolved_and_unreferenced_symbols())
    assert dedent('''
        from os.path import basename


        # Some function
        def func(n):
            print(basename(n))
        ''').strip() == new_src


def test_imports_removes_unused(index):
    src = dedent('''
        import sys

        def func(n):
            print(basename(n))
        ''').strip()
    scope = Scope.from_source(src)
    new_src = update_imports(src, index, *scope.find_unresolved_and_unreferenced_symbols())
    assert dedent('''
        from os.path import basename


        def func(n):
            print(basename(n))
        ''').strip() == new_src


def test_from_import_as(index):
    src = dedent('''
        from clastic import MiddleWare as WebMiddleWare
        ''').strip()
    scope = Scope.from_source(src)
    new_src = update_imports(src, index, *scope.find_unresolved_and_unreferenced_symbols())
    assert src == new_src.strip()


def test_importer_wrapping(index):
    src = dedent('''
        from injector import Binder, Injector, InstanceProvider, Key, MappingKey, Module, Scope, ScopeDecorator, SequenceKey, inject, provides, singleton
        from waffle import stuff

        Binder, Injector, InstanceProvider, Key, MappingKey, Module, Scope, ScopeDecorator, SequenceKey, inject, provides, singleton, stuff
        ''').strip()
    expected_src = dedent('''
        from injector import Binder, Injector, InstanceProvider, Key, MappingKey, \\
            Module, Scope, ScopeDecorator, SequenceKey, inject, provides, singleton
        from waffle import stuff


        Binder, Injector, InstanceProvider, Key, MappingKey, Module, Scope, ScopeDecorator, SequenceKey, inject, provides, singleton, stuff
        ''').strip()

    scope = Scope.from_source(src)
    new_src = update_imports(src, index, *scope.find_unresolved_and_unreferenced_symbols()).strip()
    assert expected_src == new_src


def test_importer_directives(index):
    src = dedent('''
        from gevent.monkey import patch_all; patch_all()

        # importmagic: manage
        import re
        import sys

        print(os.path.basename('moo'))
        ''').strip()
    expected_src = dedent('''
        from gevent.monkey import patch_all; patch_all()

        # importmagic: manage
        import os.path


        print(os.path.basename('moo'))
        ''').strip()
    scope = Scope.from_source(src)
    new_src = update_imports(src, index, *scope.find_unresolved_and_unreferenced_symbols()).strip()
    assert expected_src == new_src
