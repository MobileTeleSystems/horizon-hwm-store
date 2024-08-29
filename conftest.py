# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
import os
import secrets
from collections import namedtuple
from datetime import date, datetime

import pytest
from etl_entities.hwm import (
    ColumnDateHWM,
    ColumnDateTimeHWM,
    ColumnIntHWM,
    FileListHWM,
    KeyValueIntHWM,
)
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
                # no source
                expression=secrets.token_hex(5),
                value=10,
            ),
            15,
        ),
        (
            ColumnIntHWM(
                name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
                source=secrets.token_hex(5),
                expression=secrets.token_hex(5),
                value=10,
            ),
            15,
        ),
        (
            ColumnDateHWM(
                name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
                source=secrets.token_hex(5),
                expression=secrets.token_hex(5),
                value=date(year=2023, month=8, day=15),
            ),
            date(year=2023, month=9, day=15),  # + 1 month
        ),
        (
            ColumnDateTimeHWM(
                name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
                source=secrets.token_hex(5),
                expression=secrets.token_hex(5),
                value=datetime(year=2023, month=8, day=15, hour=11, minute=22, second=33),
            ),
            datetime(year=2023, month=8, day=15, hour=11, minute=23, second=33),  # + 1 minute
        ),
        (
            FileListHWM(
                name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
                # no directory
                value=["/some/file1", "/another/file2"],
            ),
            ["/some/file1", "/another/file2", "/more/file3"],
        ),
        (
            FileListHWM(
                name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
                directory="/absolute/path",
                value=["/absolute/path/file1", "/absolute/path/file2"],
            ),
            ["/absolute/path/file1", "/absolute/path/file2", "/absolute/path/file3"],
        ),
        (
            KeyValueIntHWM(
                name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
                # no topic
                expression="offset",
                value={
                    "0": 100,
                    "1": 123,
                },
            ),
            {
                "0": 110,
                "1": 150,
            },
        ),
        (
            KeyValueIntHWM(
                name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
                topic="topic_name",
                expression="offset",
                value={
                    "0": 100,
                    "1": 123,
                },
            ),
            {
                "0": 110,
                "1": 150,
            },
        ),
    ],
)
def hwm_new_value(request):
    return request.param


@pytest.fixture
def hwm_store():
    return HorizonHWMStore(
        api_url=HORIZON_URL,
        auth=LoginPassword(login=HORIZON_USER, password=HORIZON_PASSWORD),
        namespace=HORIZON_NAMESPACE,
    )


@pytest.fixture(scope="module")
def ensure_namespace():
    from requests.exceptions import HTTPError

    store = HorizonHWMStore(
        api_url=HORIZON_URL,
        auth=LoginPassword(login=HORIZON_USER, password=HORIZON_PASSWORD),
        namespace=HORIZON_NAMESPACE,
    )

    try:
        store.client.create_namespace(NamespaceCreateRequestV1(name=HORIZON_NAMESPACE))  # noqa: WPS437
    except HTTPError:
        # exception: 409 Client Error: Conflict for url: http://horizon/v1/namespaces/ - namespace already exists
        pass
