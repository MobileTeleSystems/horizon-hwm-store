import logging
import secrets

import pytest
from etl_entities.hwm_store import HWMStoreStackManager
from horizon.client.auth import LoginPassword

from horizon_hwm_store import HorizonHWMStore


@pytest.mark.parametrize(
    "username, password, auth, namespace, err_msg",
    [
        (
            "user",
            secrets.token_hex(),
            True,
            None,
            "error for HorizonHWMStore\nnamespace\n  none is not an allowed value",
        ),
        (
            "user",
            secrets.token_hex(),
            False,
            secrets.token_hex(),
            "HorizonHWMStore\nauth\n  none is not an allowed value",
        ),
        (None, None, True, secrets.token_hex(), "LoginPassword\nlogin\n  none is not an allowed value"),
        ("user", None, True, secrets.token_hex(), " LoginPassword\npassword\n  none is not an allowed value"),
    ],
)
def test_validation_errors(username, password, auth, namespace, err_msg):
    with pytest.raises(ValueError, match=err_msg):
        HorizonHWMStore(
            api_url="http://some.domain.com",
            auth=LoginPassword(login=username, password=password) if auth else None,
            namespace=namespace,
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
    assert "url = 'http://some.domain.com'" in caplog.text
    assert "auth = " in caplog.text
    assert password not in caplog.text


def test_horizon_hwm_no_schema(caplog):
    with pytest.raises(ValueError, match="invalid or missing URL scheme"):
        HorizonHWMStore(
            api_url="some.domain.com",
            auth=LoginPassword(login=secrets.token_hex(), password=secrets.token_hex()),
            namespace=secrets.token_hex(),
        )
