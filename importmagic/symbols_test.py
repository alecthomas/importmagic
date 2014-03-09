import pdb
from textwrap import dedent

from importmagic.symbols import Scope, _symbol_series


def test_parser_symbol_in_global_function():
    src = dedent('''
        import posixpath
        import os as thisos

        class Class(object):
            def foo(self):
                print(self.bar)

        def basename_no_ext(filename, default=1):
            def inner():
                print(basename)

            basename, _ = os.path.splitext(os.path.basename(filename))
            moo = 10
            inner()

            with open('foo') as fd:
                print(fd.read())

            try:
                print('foo')
            except Exception as e:
                print(e)

        basename_no_ext(sys.path)

        for path in sys.path:
            print(path)

        sys.path[0] = 10

        moo = lambda a: True

        comp = [p for p in sys.path]

        sys.path[10] = 2

        posixpath.join(['a', 'b'])


        ''')
    symbols, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert symbols == set(['sys.path', 'os.path.splitext', 'os.path.basename'])


def test_deep_package_reference_with_function_call():
    src = dedent('''
        print(os.path.dirname('src/python'))
        ''')
    symbols, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert symbols == set(['os.path.dirname'])


def test_deep_package_reference_with_subscript():
    src = dedent('''
        print(sys.path[0])
        ''')
    symbols, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert symbols == set(['sys.path'])


def test_parser_class_methods_namespace_correctly():
    src = dedent('''
        class Class(object):
            def __init__(self):
                self.value = 1
                get_value()  # Should be unresolved

            def get_value(self):
                return self.value

            def set_value(self, value):
                self.value = value

            setter = set_value  # Should be resolved
        ''')
    unresolved, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['get_value'])


def test_path_from_node_function():
    src = dedent('''
        os.path.basename(waz).tolower()
        ''')
    unresolved, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['waz', 'os.path.basename'])


def test_path_from_node_subscript():
    src = dedent('''
        sys.path[0].tolower()
        ''')
    unresolved, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['sys.path'])


def test_symbol_series():
    assert _symbol_series('os.path.basename') == ['os', 'os.path', 'os.path.basename']


def test_symbol_from_nested_tuples():
    src = dedent("""
        a = (os, (os.path, sys))
        """)
    symbols, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert symbols == set(['os', 'os.path', 'sys'])


def test_symbol_from_decorator():
    src = dedent("""
        @foo.bar(a=waz)
        def bar(): pass
        """)
    symbols, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert symbols == set(['foo.bar', 'waz'])


def test_referenced_symbols_from_decorated_function():
    src = dedent("""
        @foo.bar
        def bar():
            print(waz)
            print(baz)
        """)
    symbols, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert symbols == set(['foo.bar', 'waz', 'baz'])


def test_find_unresolved_and_unreferenced_symbols():
    src = dedent("""
        import os
        import sys
        import urllib2
        from os.path import basename

        def f(p):
            def b():
                f = 10
                print(f)
            return basename(p)

        class A(object):
            etc = os.walk('/etc')

            def __init__(self):
                print(sys.path, urllib.urlquote('blah'))

        """).strip()
    scope = Scope.from_source(src)
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['urllib.urlquote'])
    assert unreferenced == set(['A', 'urllib2', 'f'])


class TestSymbolCollection(object):
    def _collect(self, src, include_unreferenced=False):
        scope = Scope.from_source(src)
        unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
        if include_unreferenced:
            return unresolved, unreferenced
        return unresolved

    def test_attribute(self):
        assert self._collect('foo.bar') == set(['foo.bar'])

    def test_tuple(self):
        assert self._collect('(foo, bar, (waz, foo))') == set(['foo', 'bar', 'foo', 'waz'])

    def test_chained_calls(self):
        assert self._collect('foo(bar).waz(baz)') == set(['foo', 'bar', 'baz'])

    def test_chained_subscript(self):
        assert self._collect('foo[bar].waz(baz).asdf()') == set(['foo', 'bar', 'baz'])

    def test_attribute_then_call(self):
        assert self._collect('foo.bar(waz)') == set(['foo.bar', 'waz'])

    def test_deep_attributes(self):
        assert self._collect('foo.bar.waz') == set(['foo.bar.waz'])

    def test_generator(self):
        assert self._collect('(i for b in c)') == set(['i', 'c'])

    def test_comprehension(self):
        assert self._collect('[i for b in c]') == set(['i', 'c'])

    def test_class_attribute(self):
        assert self._collect('class A:\n  a = b') == set(['b'])

    def test_with(self):
        assert self._collect('with a: pass') == set(['a'])

    def test_with_variables(self):
        assert self._collect('def a():\n  with a as b: pass', include_unreferenced=True) == (set(), set())

    def test_assignment_in_for(self):
        assert self._collect('def a():\n  for i in [1, 2]: b = 10', include_unreferenced=True) == (set(), set(['a']))

    def test_assignment_to_subscript(self):
        assert self._collect('a[10] = 10', include_unreferenced=True) == (set(['a']), set())

    def test_attribute_calls(self):
        assert self._collect('a().b().c()') == set(['a'])

    def test_attribute_calls_with_args(self):
        assert self._collect('a(d).b(e).c(f.g)') == set(['a', 'd', 'e', 'f.g'])
