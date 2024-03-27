import logging
import secrets

import pytest
from etl_entities.hwm_store import HWMStoreStackManager
from horizon.client.auth import LoginPassword

from horizon_hwm_store import HorizonHWMStore


def test_validation_errors():
    with pytest.raises(ValueError, match="none is not an allowed value"):
        HorizonHWMStore(
            api_url="http://some.domain.com",
            auth=LoginPassword(login="user", password=secrets.token_hex()),
            namespace=None,
        )

    with pytest.raises(
        ValueError,
        match=".*(expected dict not NoneType|Input should be a valid dictionary or instance of LoginPassword).*",
    ):
        HorizonHWMStore(
            api_url="http://some.domain.com",
            auth=None,
            namespace=secrets.token_hex(),
        )

    with pytest.raises(
        ValueError,
        match=".*(none is not an allowed value|Input should be a valid string).*",
    ):
        HorizonHWMStore(
            api_url="http://some.domain.com",
            auth=LoginPassword(login=None, password=secrets.token_hex()),
            namespace=secrets.token_hex(),
        )

    with pytest.raises(
        ValueError,
        match=".*(none is not an allowed value|Input should be a valid string).*",
    ):
        HorizonHWMStore(
            api_url="http://some.domain.com",
            auth=LoginPassword(login="user", password=None),
            namespace=secrets.token_hex(),
        )


def test_horizon_hwm_store_init(caplog):
    user = secrets.token_hex()
    password = secrets.token_hex()
    namespace = secrets.token_hex()
    hwm_store = HorizonHWMStore(
        api_url="http://some.domain.com",
        auth=LoginPassword(login=user, password=password),
        namespace=namespace,
    )

    assert hwm_store.api_url == "http://some.domain.com"
    assert hwm_store.auth.login == user
    assert hwm_store.namespace == namespace
    assert hwm_store.auth.password != password
    assert hwm_store.auth.password.get_secret_value() == password

    with caplog.at_level(logging.INFO):
        with hwm_store as store:
            assert HWMStoreStackManager.get_current() == store

    assert "Using HorizonHWMStore as HWM Store" in caplog.text
    assert "'http://some.domain.com'" in caplog.text
    assert "auth = " in caplog.text
    assert password not in caplog.text


def test_horizon_hwm_no_schema():
    with pytest.raises(ValueError, match="invalid or missing URL scheme"):
        HorizonHWMStore(
            api_url="some.domain.com",
            auth=LoginPassword(login=secrets.token_hex(), password=secrets.token_hex()),
            namespace=secrets.token_hex(),
        )
