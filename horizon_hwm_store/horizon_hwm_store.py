# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Optional

from etl_entities.hwm import HWM, HWMTypeRegistry
from etl_entities.hwm_store import BaseHWMStore, register_hwm_store_class
from horizon.client.auth import LoginPassword
from horizon.client.sync import HorizonClientSync, RetryConfig, TimeoutConfig
from horizon.commons.schemas.v1 import (
    HWMCreateRequestV1,
    HWMPaginateQueryV1,
    HWMUpdateRequestV1,
    NamespacePaginateQueryV1,
)
from pydantic import Field, PrivateAttr


@register_hwm_store_class("horizon")
class HorizonHWMStore(BaseHWMStore):
    """
    Fetch/store High Water Mark (HWM) values from the Horizon REST API.

    .. warning::

        It is required to create namespace in Horizon BEFORE using this class.

    Parameters
    ----------
    api_url : str
        The base URL of the Horizon REST API.

    auth : :obj:`horizon.client.auth.LoginPassword`
        Auth credentials.

    namespace : str
        The namespace under which the HWMs will be stored and managed.

    retry : :obj:`horizon.client.sync.RetryConfig`
        Configuration for request retries.

    timeout : :obj:`horizon.client.sync.TimeoutConfig`
        Configuration for request timeouts.

    Examples
    --------

    Preparation:

    .. code:: python

        from onetl.connection import Hive, Postgres
        from onetl.core import DBReader
        from onetl.strategy import IncrementalStrategy

        spark = ...

        postgres = Postgres(
            host="postgres.domain.com",
            user="myuser",
            password="*****",
            database="target_database",
            spark=spark,
        )

        hive = Hive(spark=spark)

        reader = DBReader(
            connection=postgres,
            source="public.mydata",
            columns=["id", "data"],
            hwm=DBReader.AutoDetectHWM(hwm="some_unique_hwm_name", expression="id"),
        )

        writer = DBWriter(connection=hive, target="newtable")

    Use raw ``HorizonHWMStore`` class:

    .. code:: python

        from horizon_hwm_store import HorizonHWMStore
        from horizon.client.auth import LoginPassword
        from horizon.client.sync import RetryConfig, TimeoutConfig

        with HorizonHWMStore(
            api_url="http://horizon-server.domain/api",
            auth=LoginPassword(login="ldap_login", password="ldap_password"),
            namespace="namespace",
            retry=RetryConfig(total=5),
            timeout=TimeoutConfig(request_timeout=10),
        ):
            with IncrementalStrategy():
                df = reader.run()
                writer.run(df)

        # will store HWM value in Horizon

    Use ``@detect_hwm_store`` decorator:

    .. code-block:: yaml
        :caption: conf/env/prod.yaml

        hwm_store:
            horizon:
                api_url: http://horizon-server.domain/api
                namespace: namespace
                auth:
                    type: login_password
                    login: ldap_login
                    password: ldap_password
                retry:
                    total: 5
                timeout:
                    request_timeout: 10

    .. code-block:: python
        :caption: pipelines/my_pipeline.py

        import hydra

        from etl_entities.hwm_store import detect_hwm_store


        @hydra.main(config_path="../../conf", config_name="config")
        @detect_hwm_store(config, key="hwm_store")
        def main(config):
            reader = DBReader(...)
            writer = DBWriter(...)

            with IncrementalStrategy():
                df = reader.run()
                writer.run(df)

            # will create/update HWM value in Horizon

    """

    api_url: str
    auth: LoginPassword
    namespace: str
    retry: RetryConfig = Field(default_factory=RetryConfig)
    timeout: TimeoutConfig = Field(default_factory=TimeoutConfig)
    _client: HorizonClientSync = PrivateAttr()
    _namespace_id: Optional[int] = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = HorizonClientSync(  # noqa: WPS601
            base_url=self.api_url,
            auth=self.auth,
            retry=self.retry,
            timeout=self.timeout,
        )
        self._namespace_id = None  # noqa: WPS601

    def get_hwm(self, name: str) -> Optional[HWM]:
        namespace_id = self._get_namespace_id()
        hwm_id = self._get_hwm_id(namespace_id, name)
        if hwm_id is None:
            return None

        hwm = self._client.get_hwm(hwm_id)
        hwm_data = hwm.dict(exclude={"id", "namespace_id", "changed_by", "changed_at"})
        hwm_data["modified_time"] = hwm.changed_at
        return HWMTypeRegistry.parse(hwm_data)

    def set_hwm(self, hwm: HWM) -> str:
        namespace_id = self._get_namespace_id()

        hwm_dict = hwm.serialize()
        hwm_dict["namespace_id"] = namespace_id

        hwm_id = self._get_hwm_id(namespace_id, hwm.name)  # type: ignore
        if hwm_id is None:
            create_request = HWMCreateRequestV1.parse_obj(hwm_dict)
            response = self._client.create_hwm(create_request)
        else:
            update_request = HWMUpdateRequestV1.parse_obj(hwm_dict)
            response = self._client.update_hwm(hwm_id, update_request)

        # TODO: update response string after implementing UI
        return f"{self._client.base_url}/v1/hwm/{response.id}"

    def check(self) -> HorizonHWMStore:
        """
        Perform a health check by making a request to the Horizon server.

        This method calls the 'whoami' endpoint of the Horizon client. It's used to verify
        if the backend is accessible and if the provided credentials are correct. The method
        will raise an error if the backend is unreachable, if incorrect credentials are provided,
        or if the user account is blocked.

        Method also checks whether specified namespace exists, and raises exception if not.

        Returns
        -------
        HorizonHWMStore
            Self

        """
        self._client.whoami()
        self._get_namespace_id()
        return self

    def _get_namespace_id(self) -> int:
        """
        Fetch the ID of the namespace. Raises an exception if the namespace doesn't exist.

        Returns
        -------
        int
            The ID of the namespace.

        Raises
        ------
        RuntimeError
            If the namespace does not exist.
        """
        if self._namespace_id is not None:
            return self._namespace_id

        namespaces = self._client.paginate_namespaces(NamespacePaginateQueryV1(name=self.namespace)).items
        if not namespaces:
            raise RuntimeError(f"Namespace {self.namespace!r} not found. Please create it before using.")

        self._namespace_id = namespaces[0].id  # noqa: WPS601
        return self._namespace_id

    def _get_hwm_id(self, namespace_id: int, hwm_name: str) -> Optional[int]:
        """
        Fetch the ID of the HWM within the given namespace.

        Parameters
        ----------
        namespace_id : int
            The ID of the namespace.
        hwm_name : str
            The name of the HWM.

        Returns
        -------
        Optional[int]
            The ID of the HWM, or None if it does not exist.
        """
        hwm_query = HWMPaginateQueryV1(namespace_id=namespace_id, name=hwm_name)
        hwms = self._client.paginate_hwm(hwm_query).items
        return hwms[-1].id if hwms else None
