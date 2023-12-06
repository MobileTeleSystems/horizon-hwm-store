import os
import secrets
from collections import namedtuple
from datetime import date, datetime, timedelta

import pytest
from etl_entities.hwm import ColumnDateHWM, ColumnDateTimeHWM, ColumnIntHWM, FileListHWM
from horizon.client.auth import LoginPassword
from horizon.commons.schemas.v1 import NamespaceCreateRequestV1

from horizon_hwm_store import HorizonHWMStore

PreparedDbInfo = namedtuple("PreparedDbInfo", ["full_name", "schema", "table"])

HORIZON_HOST = os.environ.get("HORIZON_HOST")
HORIZON_PORT = os.environ.get("HORIZON_PORT")
HORIZON_URL = f"http://{HORIZON_HOST}:{HORIZON_PORT}"
HORIZON_USER = os.environ.get("HORIZON_USER")
HORIZON_PASSWORD = os.environ.get("HORIZON_PASSWORD")
HORIZON_NAMESPACE = os.environ.get("HORIZON_NAMESPACE")


@pytest.fixture(
    params=[
        (
            ColumnIntHWM(
                name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
                column=secrets.token_hex(5),
                value=10,
            ),
            5,
        ),
        (
            ColumnDateHWM(
                name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
                column=secrets.token_hex(5),
                value=date(year=2023, month=8, day=15),
            ),
            timedelta(days=31),
        ),
        (
            ColumnDateTimeHWM(
                name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
                column=secrets.token_hex(5),
                value=datetime(year=2023, month=8, day=15, hour=11, minute=22, second=33),
            ),
            timedelta(seconds=50),
        ),
        (
            FileListHWM(
                name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
                directory=f"/absolute/{secrets.token_hex(5)}",
                value=["some/path", "another.file"],
            ),
            "third.file",
        ),
    ],
)
def hwm_delta(request):
    return request.param


@pytest.fixture
def hwm_store():
    return HorizonHWMStore(
        api_url=HORIZON_URL,
        auth=LoginPassword(login=HORIZON_USER, password=HORIZON_PASSWORD),
        namespace=HORIZON_NAMESPACE,
    )


@pytest.fixture(scope="module")
def namespace_exists():
    from requests.exceptions import HTTPError

    store = HorizonHWMStore(
        api_url=HORIZON_URL,
        auth=LoginPassword(login=HORIZON_USER, password=HORIZON_PASSWORD),
        namespace=HORIZON_NAMESPACE,
    )

    try:
        store._client.create_namespace(NamespaceCreateRequestV1(name=HORIZON_NAMESPACE))  # noqa: WPS437
    except HTTPError:
        # exception: 409 Client Error: Conflict for url: http://horizon/v1/namespaces/ - namespace already exists
        pass
