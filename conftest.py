import os
import secrets
from collections import namedtuple
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import Mock

import etl_entities
import pytest
from etl_entities.hwm import (
    ColumnDateHWM,
    ColumnDateTimeHWM,
    ColumnIntHWM,
    FileListHWM,
    KeyValueIntHWM,
)
from horizon.client.auth import LoginPassword
from packaging.version import Version

from horizon_hwm_store import HorizonHWMStore

PreparedDbInfo = namedtuple("PreparedDbInfo", ["full_name", "schema", "table"])

HORIZON_HOST = os.environ.get("HORIZON_HOST")
HORIZON_PORT = os.environ.get("HORIZON_PORT")
HORIZON_URL = f"http://{HORIZON_HOST}:{HORIZON_PORT}"
HORIZON_USER = os.environ.get("HORIZON_USER")
HORIZON_PASSWORD = os.environ.get("HORIZON_PASSWORD")
HORIZON_NAMESPACE = os.environ.get("HORIZON_NAMESPACE")

HWMS_WITH_VALUE = [
    (
        ColumnIntHWM(
            name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",  # noqa: WPS204
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
                0: 100,
                1: 123,
            },
        ),
        {
            0: 110,
            1: 150,
        },
    ),
    (
        KeyValueIntHWM(
            name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
            topic="topic_name",
            expression="offset",
            value={
                0: 100,
                1: 123,
            },
        ),
        {
            0: 110,
            1: 150,
        },
    ),
]

if Version(etl_entities.__version__) >= Version("2.5.0"):
    from etl_entities.hwm import FileModifiedTimeHWM

    def file_with_mtime(mtime: datetime) -> Path:
        result = Mock(spec=Path)
        result.exists.return_value = True
        result.is_file.return_value = True
        result_stat = Mock(spec=os.stat_result)
        result_stat.st_mtime = mtime.timestamp()
        result.stat.return_value = result_stat
        return result

    HWMS_WITH_VALUE.extend(
        [
            (
                FileModifiedTimeHWM(
                    name=secrets.token_hex(5),
                    # no directory
                    value=datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=timezone.utc),
                ),
                file_with_mtime(datetime(2025, 1, 1, 22, 33, 44, 567890, tzinfo=timezone.utc)),
            ),
            (
                FileModifiedTimeHWM(
                    name=secrets.token_hex(5),
                    directory="/absolute/path",
                    value=datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=timezone.utc),
                ),
                file_with_mtime(datetime(2025, 1, 1, 22, 33, 44, 567890, tzinfo=timezone.utc)),
            ),
        ],
    )


@pytest.fixture(params=HWMS_WITH_VALUE)
def hwm_new_values(request):
    return request.param


@pytest.fixture(params=[HWMS_WITH_VALUE[0]])
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

    HorizonHWMStore(
        api_url=HORIZON_URL,
        auth=LoginPassword(login=HORIZON_USER, password=HORIZON_PASSWORD),
        namespace=HORIZON_NAMESPACE,
    ).force_create_namespace()
