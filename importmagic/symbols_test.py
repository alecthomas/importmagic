import sys
from textwrap import dedent

import pytest
from importmagic.six import u
from importmagic.symbols import Scope, _symbol_series


def test_parser_symbol_in_global_function():
    """
    Parses a symbol.

    Args:
    """
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

        comp = [p for p in sys.path if p]

        sys.path[10] = 2

        posixpath.join(['a', 'b'])


        ''')
    symbols, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert symbols == set(['sys.path', 'os.path.splitext', 'os.path.basename'])


def test_deep_package_reference_with_function_call():
    """
    Given a set of the callable reference to findable package.

    Args:
    """
    src = dedent('''
        print(os.path.dirname('src/python'))
        ''')
    symbols, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert symbols == set(['os.path.dirname'])


def test_deep_package_reference_with_subscript():
    """
    Test if a package subscript.

    Args:
    """
    src = dedent('''
        print(sys.path[0])
        ''')
    symbols, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert symbols == set(['sys.path'])


def test_parser_class_methods_namespace_correctly():
    """
    Determines the namespace methods that class namespaces.

    Args:
    """
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
    """
    Test if the path of a path.

    Args:
    """
    src = dedent('''
        os.path.basename(waz).tolower()
        ''')
    unresolved, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['waz', 'os.path.basename'])


def test_symbol_from_assignment():
    """
    Test if source is a symbol from source.

    Args:
    """
    src = dedent('''
        def f(n): sys.stderr = n
        ''')
    unresolved, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['sys.stderr'])


def test_path_from_node_subscript():
    """
    Test if the source file exists.

    Args:
    """
    src = dedent('''
        sys.path[0].tolower()
        ''')
    unresolved, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['sys.path'])


def test_symbol_series():
    """
    Èi̇·åıĸæį¢æī·

    Args:
    """
    assert _symbol_series('os.path.basename') == ['os', 'os.path', 'os.path.basename']


def test_symbol_in_expression():
    """
    Test if a symbol is contained in - place.

    Args:
    """
    src = dedent('''
        (db.Event.creator_id == db.Account.id) & (db.Account.user_id == bindparam('user_id'))
        ''')
    unresolved, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['db.Event.creator_id', 'db.Account.id', 'db.Account.user_id', 'bindparam'])


def test_symbol_from_nested_tuples():
    """
    Test for nested symbols.

    Args:
    """
    src = dedent("""
        a = (os, (os.path, sys))
        """)
    symbols, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert symbols == set(['os', 'os.path', 'sys'])


def test_symbol_from_argument_defaults():
    """
    Parse symbol symbols from source.

    Args:
    """
    src = dedent("""
        def f(a, b=os.path, c=os): pass
        """)

    symbols, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert symbols == set(['os.path', 'os'])


def test_symbol_from_decorator():
    """
    Test if a symbol from source.

    Args:
    """
    src = dedent("""
        @foo.bar(a=waz)
        def bar(): pass
        """)
    symbols, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert symbols == set(['foo.bar', 'waz'])


def test_referenced_symbols_from_decorated_function():
    """
    Test that all symbols in the source.

    Args:
    """
    src = dedent("""
        @foo.bar
        def bar():
            print(waz)
            print(baz)
        """)
    symbols, _ = Scope.from_source(src).find_unresolved_and_unreferenced_symbols()
    assert symbols == set(['foo.bar', 'waz', 'baz'])


def test_find_unresolved_and_unreferenced_symbols():
    """
    Find unresolved symbols that are unresolved.

    Args:
    """
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

            def exc_handler(self):
                try:
                    raise SomeException(some_value)
                except:
                    pass
                else:
                    print(SOME_MSG)

            def cond(self, *args, **kwds):
                if cond:
                    pass
                elif cond2:
                    print('foo')
                while cond3:
                    print(kwds)

        """).strip()
    scope = Scope.from_source(src)
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['urllib.urlquote', 'SomeException', 'some_value',
                              'SOME_MSG', 'cond', 'cond2', 'cond3'])
    assert unreferenced == set(['A', 'urllib2', 'f'])


def test_accepts_unicode_strings():
    """
    Test if all unicode strings that are unresolved.

    Args:
    """
    src = dedent(u("""
        # coding: utf-8
        foo
    """)).strip()
    scope = Scope.from_source(src)
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['foo'])

@pytest.mark.skipif(sys.version_info < (3, 0), reason="requires python3")
def test_annotations_without_imports():
    """
    Unresolved imports are imported.

    Args:
    """
    src = dedent("""
        def print_it(it: Iterable):
            for i in it:
                method1(i)
        print_it(['a', 'b', 'c'])
        """)
    scope = Scope.from_source(src)
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['method1', 'Iterable'])
    assert unreferenced == set([])

@pytest.mark.skipif(sys.version_info < (3, 0), reason="requires python3")
def test_annotations_with_imports():
    """
    Test if source imports.

    Args:
    """
    src = dedent("""
        from typing import Iterable

        def print_it(it: Iterable):
            for i in it:
                print(i)
        """)
    scope = Scope.from_source(src)
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
    assert unresolved == set([])
    assert unreferenced == set(['print_it'])

@pytest.mark.skipif(sys.version_info < (3, 5), reason="requires python3.5")
def test_annotations_complex():
    """
    Test for complex annotations.

    Args:
    """
    # https://www.python.org/dev/peps/pep-3107/
    src = dedent("""
        def foo(a: 'x', b: 5 + 6, c: list, \
            d: Iterable, e: CustomType) -> max(2, 9):
                print(a)
        
        foo()
        """)
    scope = Scope.from_source(src)
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['Iterable', 'CustomType'])
    assert unreferenced == set([])

@pytest.mark.skipif(sys.version_info < (3, 5), reason="requires python3.5")
def test_annotations_return_type():
    """
    Determine type of the given type.

    Args:
    """
    # https://www.python.org/dev/peps/pep-3107/
    src = dedent("""
        def foo(a) -> CustomType:
            print(a)
        
        foo()
        """)
    scope = Scope.from_source(src)
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['CustomType'])
    assert unreferenced == set([])

@pytest.mark.skipif(sys.version_info < (3, 5), reason="requires python3.5")
def test_annotations_from_typing():
    """
    Test if the annotations in the annotations.

    Args:
    """
    src = dedent("""
        from typing import Dict, Tuple

        Vector = List[float]

        def scale(scalar: float, vector: Vector) -> Vector:
            return [scalar * num for num in vector]

        new_vector = scale(2.0, [1.0, -4.2, 5.4])
        print(new_vector)
        """)
    scope = Scope.from_source(src)
    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
    assert unresolved == set(['List'])
    assert unreferenced == set(['Tuple', 'Dict'])

class TestSymbolCollection(object):
    def _collect(self, src, include_unreferenced=False):
        """
        Collect all symbols from source.

        Args:
            self: (todo): write your description
            src: (todo): write your description
            include_unreferenced: (bool): write your description
        """
        scope = Scope.from_source(src)
        unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
        if include_unreferenced:
            return unresolved, unreferenced
        return unresolved

    def test_attribute(self):
        """
        Sets the test attribute.

        Args:
            self: (todo): write your description
        """
        assert self._collect('foo.bar') == set(['foo.bar'])

    def test_tuple(self):
        """
        Collect test test test test case.

        Args:
            self: (todo): write your description
        """
        assert self._collect('(foo, bar, (waz, foo))') == set(['foo', 'bar', 'foo', 'waz'])

    def test_chained_calls(self):
        """
        Check if the test test.

        Args:
            self: (todo): write your description
        """
        assert self._collect('foo(bar).waz(baz)') == set(['foo', 'bar', 'baz'])

    def test_chained_subscript(self):
        """
        Runs all submissions of this changelist.

        Args:
            self: (todo): write your description
        """
        assert self._collect('foo[bar].waz(baz).asdf()') == set(['foo', 'bar', 'baz'])

    def test_attribute_then_call(self):
        """
        Sets the test test execution.

        Args:
            self: (todo): write your description
        """
        assert self._collect('foo.bar(waz)') == set(['foo.bar', 'waz'])

    def test_deep_attributes(self):
        """
        Collect all test attributes.

        Args:
            self: (todo): write your description
        """
        assert self._collect('foo.bar.waz') == set(['foo.bar.waz'])

    def test_generator(self):
        """
        Generate the test generator.

        Args:
            self: (todo): write your description
        """
        assert self._collect('(i for b in c)') == set(['i', 'c'])

    def test_comprehension(self):
        """
        Run test test test test.

        Args:
            self: (todo): write your description
        """
        assert self._collect('[i for b in c]') == set(['i', 'c'])

    def test_class_attribute(self):
        """
        Sets the test class attribute of the class.

        Args:
            self: (todo): write your description
        """
        assert self._collect('class A:\n  a = b') == set(['b'])

    def test_with(self):
        """
        Run test test test test.

        Args:
            self: (todo): write your description
        """
        assert self._collect('with a: pass') == set(['a'])

    def test_with_variables(self):
        """
        Sets all variables in the set.

        Args:
            self: (todo): write your description
        """
        assert self._collect('def a():\n  with a as b: pass', include_unreferenced=True) == (set(), set())

    def test_assignment_in_for(self):
        """
        Assigns the assignment of the current test.

        Args:
            self: (todo): write your description
        """
        assert self._collect('def a():\n  for i in [1, 2]: b = 10', include_unreferenced=True) == (set(), set(['a']))

    def test_assignment_to_subscript(self):
        """
        Test if the given subscript to the given test.

        Args:
            self: (todo): write your description
        """
        assert self._collect('a[10] = 10', include_unreferenced=True) == (set(['a']), set())

    def test_attribute_calls(self):
        """
        Determine whether the test calls.

        Args:
            self: (todo): write your description
        """
        assert self._collect('a().b().c()') == set(['a'])

    def test_attribute_calls_with_args(self):
        """
        Test if the test calls to the test.

        Args:
            self: (todo): write your description
        """
        assert self._collect('a(d).b.h(e).c(f.g)') == set(['a', 'd', 'e', 'f.g'])

    def test_subscript_with_attrs(self):
        """
        Runs the test test.

        Args:
            self: (todo): write your description
        """
        assert self._collect('a[h].b.c.d[e.f.g]()') == set(['a', 'h', 'e.f.g'])

    def test_multiple_names(self):
        """
        Collect all possible test names.

        Args:
            self: (todo): write your description
        """
        assert self._collect('a == b') == set(['a', 'b'])

    def test_multiple_attributes(self):
        """
        : return : attr : attr : set

        Args:
            self: (todo): write your description
        """
        assert self._collect('a.c == b.d') == set(['a.c', 'b.d'])
