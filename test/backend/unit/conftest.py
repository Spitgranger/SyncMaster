from unittest.mock import patch

import pytest

from .fixtures.api_gateway_event_v1 import *
from .fixtures.s3 import *


@pytest.fixture(autouse=True)
def disable_ttl_cache_decorator():
    # Patch the cachetools.ttl_cache decorator to do nothing
    with patch("cachetools.func.ttl_cache", lambda *args, **kwargs: lambda f: f):
        yield
