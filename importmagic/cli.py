"""Update python imports using importmagic."""

import argparse
import os
import sys

import importmagic


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file_name')
    parser.add_argument(
        '--refresh',
        action='store_true',
        help='If set, forces a refresh of the importmagic index.'
    )
    parser.add_argument(
        '--exclude-current-path',
        action='store_true',
        help='If set, will not automatically add the current directory'
        ' to the import path when building the index.'
    )

    args = parser.parse_args()

    path = sys.path if args.exclude_current_path else sys.path + [os.getcwd()]

    index = importmagic.SymbolIndex()
    index.get_or_create_index(paths=path, refresh=args.refresh)

    with open(args.file_name) as f:
        python_source = f.read()

    scope = importmagic.Scope.from_source(python_source)

    unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
    python_source = importmagic.update_imports(python_source, index, unresolved, unreferenced)

    with open(args.file_name, 'w') as f:
        f.write(python_source)


if __name__ == '__main__':
    main()
