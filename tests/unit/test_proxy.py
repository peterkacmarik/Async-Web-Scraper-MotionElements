import pytest
from proxy import _get_proxy, _test_proxy, _get_working_proxies


def test_get_proxy():
    proxy_list: list = _get_proxy()
    assert len(proxy_list) == 10
    assert isinstance(proxy_list, list)
    assert all(isinstance(proxy, str) for proxy in proxy_list)

@pytest.fixture
async def proxy():
    return 'http://20.206.106.192:8123'

@pytest.mark.asyncio
async def test_test_proxy(proxy):
    p = await proxy
    proxy = await _test_proxy(p)
    assert proxy is not None
    assert isinstance(proxy, str)
    assert 'http://' in proxy


@pytest.fixture
def proxies():
    return _get_proxy()

@pytest.mark.asyncio
async def test_get_working_proxies(proxies):
    working_proxies = await _get_working_proxies(proxies)
    assert working_proxies is not None
    assert len(working_proxies) > 0
    assert isinstance(working_proxies, list)
    assert all(isinstance(proxy, str) for proxy in working_proxies)
    


