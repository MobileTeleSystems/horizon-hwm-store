#  Copyright 2023 MTS (Mobile Telesystems)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


from typing import Optional

from etl_entities.hwm import HWM, HWMTypeRegistry
from etl_entities.hwm_store import BaseHWMStore, register_hwm_store_class
from horizon.client.auth import LoginPassword
from horizon.client.sync import HorizonClientSync
from horizon.commons.schemas.v1 import (
    HWMCreateRequestV1,
    HWMPaginateQueryV1,
    HWMUpdateRequestV1,
    NamespacePaginateQueryV1,
)
from pydantic import PrivateAttr


@register_hwm_store_class("horizon")
class HorizonHWMStore(BaseHWMStore):
    """
    HorizonHWMStore is a class for storing and retrieving High Water Mark (HWM) values using the Horizon server.
    This class allows for interactions with a Horizon server to manage HWM values within a specified namespace.

    Parameters
    -----------
    api_url : str
        The base URL of the Horizon server.

    auth : LoginPassword
        An instance of a Horizon Auth class, such as `horizon.client.auth.LoginPassword`.

    namespace : str
        The namespace under which the HWMs will be stored and managed.


    Examples
    --------
    .. code:: python

        from onetl.connection import Hive, Postgres
        from onetl.core import DBReader
        from onetl.strategy import IncrementalStrategy
        from horizon.client.auth import LoginPassword
        from horizon_hwm_store import HorizonHWMStore

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
            table="public.mydata",
            columns=["id", "data"],
            hwm=DBReader.AutoDetectHWM(hwm="some_unique_hwm_name", column="id"),
        )

        writer = DBWriter(connection=hive, table="newtable")

        with HorizonHWMStore(
            url="http://horizon-server.domain",
            auth=LoginPassword(login="ldap_login", password="ldap_password"),
            namespace="namespace",
        ):
            with IncrementalStrategy():
                df = reader.run()
                writer.run(df)

        # will store HWM value in Horizon

    """

    api_url: str
    auth: LoginPassword
    namespace: str
    _client: HorizonClientSync = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = HorizonClientSync(base_url=self.api_url, auth=self.auth)  # noqa: WPS601

    def get_hwm(self, name: str) -> Optional[HWM]:
        namespace_id = self._get_namespace_id()
        hwm_id = self._get_hwm_id(namespace_id, name)
        if hwm_id is None:
            return None

        hwm_data = self._client.get_hwm(hwm_id)
        return HWMTypeRegistry.parse(hwm_data.dict())

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

    def check(self) -> None:
        """
        Perform a health check by making a request to the Horizon server.

        This method calls the 'whoami' endpoint of the Horizon client. It's used to verify
        if the backend is accessible and if the provided credentials are correct. The method
        will raise an error if the backend is unreachable, if incorrect credentials are provided,
        or if the user account is blocked.

        """
        self._client.whoami()

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
        namespaces = self._client.paginate_namespaces(NamespacePaginateQueryV1(name=self.namespace)).items
        if not namespaces:
            raise RuntimeError(f"Namespace '{self.namespace}' not found. Please create it before using.")
        return namespaces[0].id

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
