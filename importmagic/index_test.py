from __future__ import absolute_import

import json
from textwrap import dedent

from importmagic.index import SymbolIndex


def serialize(tree):
    return json.loads(tree.serialize())


def test_index_file_with_all():
    src = dedent('''
        __all__ = ['one']

        one = 1
        two = 2
        three = 3
        ''')
    tree = SymbolIndex()
    with tree.enter('test') as subtree:
        subtree.index_source('test.py', src)
    assert serialize(subtree) == {".location": "L", ".score": 1.0, "one": 1.1}


def test_index_if_name_main():
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
    src = dedent('''
        def walk(dir): pass
        ''')
    tree = SymbolIndex()
    with tree.enter('os') as os_tree:
        with os_tree.enter('path') as path_tree:
            path_tree.index_source('os.py', src)
    assert tree.symbol_scores('walk')[0][1:] == ('os.path', 'walk')
    assert tree.symbol_scores('os') == [(1.2, 'os', None)]
    assert tree.symbol_scores('os.path.walk') == [(3.5, 'os.path', 'walk')]


def test_index_score_deep_unknown_attribute(index):
    assert index.symbol_scores('os.path.basename.unknown')[0][1:] == ('os.path', 'basename')


def test_index_score_deep_reference(index):
    assert index.symbol_scores('os.path.basename')[0][1:] == ('os.path', 'basename')


def test_index_score_missing_symbol(index):
    assert index.symbol_scores('os.path.something')[0][1:] == ('os.path', None)


def test_index_score_sys_path(index):
    index.symbol_scores('sys.path')[0] == (2.0, 'sys', 'path')


def test_encoding_score(index):
    assert index.symbol_scores('iso8859_6.Codec')[0][1:] == ('encodings.iso8859_6', 'Codec')


def test_score_boosts_apply_to_scopes(index):
    print(index.symbol_scores('basename'))
    assert index.symbol_scores('basename')[0][1:] == ('os.path', 'basename')
