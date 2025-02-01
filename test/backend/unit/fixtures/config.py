import pytest
from backend.service.util import create_client_with_role, create_resource_with_role


@pytest.fixture(autouse=True)
def clear_cache():
    yield
    # Clear the cache for any function decorated with a cache after a test has run
    create_resource_with_role.cache.clear()
    create_client_with_role.cache.clear()
