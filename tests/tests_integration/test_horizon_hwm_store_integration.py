import os

import pytest
from horizon.client.auth import LoginPassword
from requests.exceptions import ConnectionError

from horizon_hwm_store import HorizonHWMStore

HORIZON_HOST = os.environ.get("HORIZON_HOST")
HORIZON_PORT = os.environ.get("HORIZON_PORT")
HORIZON_URL = f"http://{HORIZON_HOST}:{HORIZON_PORT}"
HORIZON_USER = os.environ.get("HORIZON_USER")
HORIZON_PASSWORD = os.environ.get("HORIZON_PASSWORD")
HORIZON_NAMESPACE = os.environ.get("HORIZON_NAMESPACE")


def test_hwm_store_integration(hwm_store, hwm_delta, ensure_namespace):
    hwm, delta = hwm_delta
    assert hwm_store.get_hwm(hwm.name) is None

    hwm_store.set_hwm(hwm)
    assert hwm_store.get_hwm(hwm.name) == hwm

    hwm2 = hwm + delta
    # until `.set_hwm()` is called, HWM changes are not send to store
    assert hwm_store.get_hwm(hwm.name) == hwm

    hwm_store.set_hwm(hwm2)
    assert hwm_store.get_hwm(hwm.name) == hwm2


def test_horizon_server_unreachable(hwm_delta):
    store = HorizonHWMStore(
        api_url="http://unreachable-host",
        auth=LoginPassword(login=HORIZON_USER, password=HORIZON_PASSWORD),
        namespace=HORIZON_NAMESPACE,
    )
    hwm, _ = hwm_delta
    error_msg = "Failed to resolve 'unreachable-host'"

    with pytest.raises(ConnectionError, match=error_msg):
        store.check()

    with pytest.raises(ConnectionError, match=error_msg):
        store.get_hwm("some_hwm_name")

    with pytest.raises(ConnectionError, match=error_msg):
        store.set_hwm(hwm)


def test_hwm_store_unexisting_namespace(hwm_delta):
    store = HorizonHWMStore(
        api_url=HORIZON_URL,
        auth=LoginPassword(login=HORIZON_USER, password=HORIZON_PASSWORD),
        namespace="non_existent_namespace",
    )
    hwm, _ = hwm_delta
    error_msg = "Namespace 'non_existent_namespace' not found. Please create it before using."

    with pytest.raises(RuntimeError, match=error_msg):
        store.check()

    with pytest.raises(RuntimeError, match=error_msg):
        store.get_hwm("some_hwm_name")

    with pytest.raises(RuntimeError, match=error_msg):
        store.set_hwm(hwm)
