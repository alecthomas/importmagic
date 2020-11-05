from __future__ import absolute_import

import json
import re
from textwrap import dedent

from importmagic.index import SymbolIndex
from importmagic.six import b


def serialize(tree):
    """
    Serialize the given tree.

    Args:
        tree: (todo): write your description
    """
    return json.loads(tree.serialize())


def test_index_basic_api(index):
    """
    Test if the index of the given index.

    Args:
        index: (todo): write your description
    """
    assert index.depth() == 0
    subtree = index._tree['os']
    assert subtree.depth() == 1
    assert index.location_for('os.path') == subtree.location_for('os.path')
    assert index.find('os.walk') == subtree.find('os.walk')


def test_index_filesystem(tmpdir):
    """
    Create the indexystem index.

    Args:
        tmpdir: (str): write your description
    """
    pkg = tmpdir.mkdir('pkg')
    pkg.join('__init__.py').write('class Cls:\n pass\n')
    pkg.join('submod.py').write(dedent('''
        import sys
        import _private
        from os import path
        from other import _x

        def func():
            pass
        '''))
    with pkg.join('encoded.py').open('wb') as fp:
        fp.write(b('# encoding: latin1\ndef foo():\n print("\xff")'))
    # these should be ignored
    pkg.join('mytest_submod.py').write('def func2():\n pass\n')
    pkg.join('_submod.py').write('def func3():\n pass\n')
    pkg.join('syntaxerr.py').write('def func3():\n')
    tree = SymbolIndex(blacklist_re=re.compile('mytest_'))
    tree.build_index([str(tmpdir)])
    subtree = tree._tree['pkg']
    assert serialize(subtree) == {
        ".location": "L",
        ".score": 1.0,
        "Cls": 1.1,
        "submod": {".location": "L", ".score": 1.0,
                   "func": 1.1, "sys": 0.25, "path": 0.25},
        "encoded": {".location": "L", ".score": 1.0,
                    "foo": 1.1}}


def test_index_file_with_all():
    """
    Return the index file in the index of the source file.

    Args:
    """
    src = dedent('''
        __all__ = ['one']

        one = 1
        two = 2
        three = 3
        ''')
    tree = SymbolIndex()
    with tree.enter('test') as subtree:
        subtree.index_source('test.py', src)
    assert serialize(subtree) == {".location": "L", ".score": 1.0, "one": 1.2}


def test_index_if_name_main():
    """
    If the index of the index of the source.

    Args:
    """
    src = dedent('''
        if __name__ == '__main__':
            one = 1
        else:
            two = 2
        ''')
    tree = SymbolIndex()
    with tree.enter('test') as subtree:
        subtree.index_source('test.py', src)
    assert serialize(subtree) == {".location": "L", ".score": 1.0}


def test_index_symbol_scores():
    """
    Generate the index scores.

    Args:
    """
    src = dedent('''
        def walk(dir): pass
        ''')
    tree = SymbolIndex()
    with tree.enter('os') as os_tree:
        with os_tree.enter('path') as path_tree:
            path_tree.index_source('os.py', src)
    assert tree.symbol_scores('walk')[0][1:] == ('os.path', 'walk')
    assert tree.symbol_scores('os') == [(1.7999999999999998, 'os', None)]
    assert tree.symbol_scores('os.path.walk') == [(5.25, 'os.path', None)]


def test_index_score_deep_unknown_attribute(index):
    """
    Test if index : attr : index.

    Args:
        index: (todo): write your description
    """
    assert index.symbol_scores('os.path.basename.unknown')[0][1:] == ('os.path', None)


def test_index_score_deep_reference(index):
    """
    Compute the index of the test.

    Args:
        index: (todo): write your description
    """
    assert index.symbol_scores('os.path.basename')[0][1:] == ('os.path', None)


def test_index_score_missing_symbol(index):
    """
    Assigns the missing missing.

    Args:
        index: (todo): write your description
    """
    assert index.symbol_scores('os.path.something')[0][1:] == ('os.path', None)


def test_index_score_sys_path(index):
    """
    Test if the test index.

    Args:
        index: (todo): write your description
    """
    index.symbol_scores('sys.path')[0] == (2.0, 'sys', 'path')


def test_encoding_score(index):
    """
    Test if the scores of the same.

    Args:
        index: (todo): write your description
    """
    assert index.symbol_scores('iso8859_6.Codec')[0][1:] == ('encodings', 'iso8859_6')


def test_score_boosts_apply_to_scopes(index):
    """
    Apply scores to scores in - index.

    Args:
        index: (todo): write your description
    """
    print(index.symbol_scores('basename'))
    assert index.symbol_scores('basename')[0][1:] == ('os.path', 'basename')
