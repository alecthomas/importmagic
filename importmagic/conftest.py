import os

import pytest

from importmagic.index import SymbolIndex


@pytest.fixture(scope='session')
def index(request):
    """
    Deserializes index.

    Args:
        request: (todo): write your description
    """
    dir = os.path.dirname(__file__)
    with open(os.path.join(dir, 'test_index.json')) as fd:
        return SymbolIndex.deserialize(fd)
