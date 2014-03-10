# Import Magic

The goal of this package is to be able to automatically manage imports in Python. To that end it can:

- Build an index of all known symbols in all packages.
- Find unresolved references in source, and resolve them against the index, effectively automating imports.
- Automatically arrange imports according to PEP8.

## Using the library

Build an index:

```python
index = importmagic.index.SymbolIndex()
index.build_index(sys.path)
with open('index.json') as fd:
    index.serialize(fd)
```

Load an existing index:

```python
with open('index.json') as fd:
    index = SymbolIndex.deserialize(fd)
```

Find unresolved and unreferenced symbols:

```python
scope = importmagic.symbols.Scope.from_source(python_source)
unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
```

Print new import block:

```python
start_line, end_line, import_block = importmagic.importer.get_update(python_source, index, unresolved, unreferenced)
```

Update source code with new import blocks:

```
python_source = importmagic.importer.update_imports(python_source, index, unresolved, unreferenced)
```

For more fine-grained control over what symbols are imported, the index can be queried directly:

```python
imports = importmagic.importer.Imports(index, python_source)
imports.remove(unreferenced)

for symbol in unresolved:
    for score, module, variable in index.symbol_scores(symbol):
        if variable is None:
            imports.add_import(module)
        else:
            imports.add_import_from(module, variable)
        break

python_source = imports.update_source()
```
