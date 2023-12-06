import os

import pytest
from horizon.client.auth import LoginPassword

from horizon_hwm_store import HorizonHWMStore

HORIZON_HOST = os.environ.get("HORIZON_HOST")
HORIZON_PORT = os.environ.get("HORIZON_PORT")
HORIZON_URL = f"http://{HORIZON_HOST}:{HORIZON_PORT}"
HORIZON_USER = os.environ.get("HORIZON_USER")
HORIZON_PASSWORD = os.environ.get("HORIZON_PASSWORD")
HORIZON_NAMESPACE = os.environ.get("HORIZON_NAMESPACE")


def test_hwm_store_integration_horizon_no_access(hwm_delta):
    hwm, _delta = hwm_delta
    store = HorizonHWMStore(
        api_url="http://unknown_host_name",
        auth=LoginPassword(login=HORIZON_USER, password=HORIZON_PASSWORD),
        namespace=HORIZON_NAMESPACE,
    )

    with pytest.raises(Exception):  # noqa: B017
        store.get_hwm(hwm.qualified_name)


def test_hwm_store_integration(hwm_store, hwm_delta, namespace_exists):
    hwm, delta = hwm_delta
    assert hwm_store.get_hwm(hwm.name) is None

    hwm_store.set_hwm(hwm)
    assert hwm_store.get_hwm(hwm.name) == hwm

    hwm2 = hwm + delta
    hwm_store.set_hwm(hwm2)
    assert hwm_store.get_hwm(hwm.name) == hwm2


def test_horizon_server_unreachable():
    from requests.exceptions import ConnectionError

    store = HorizonHWMStore(
        api_url="http://unreachable-host",
        auth=LoginPassword(login=HORIZON_USER, password=HORIZON_PASSWORD),
        namespace=HORIZON_NAMESPACE,
    )

    with pytest.raises(ConnectionError, match="Failed to resolve 'unreachable-host'"):
        store.check()


def test_hwm_store_unexisting_namespace():
    store = HorizonHWMStore(
        api_url=HORIZON_URL,
        auth=LoginPassword(login=HORIZON_USER, password=HORIZON_PASSWORD),
        namespace="non_existent_namespace",
    )

    with pytest.raises(
        RuntimeError,
        match="Namespace 'non_existent_namespace' not found. Please create it before using.",
    ):
        store.get_hwm("some_hwm_name")
