import secrets

import pytest
from etl_entities.hwm_store import HWMStoreStackManager as HWMStoreManager
from etl_entities.hwm_store import detect_hwm_store
from omegaconf import OmegaConf

from horizon_hwm_store import HorizonHWMStore


@pytest.mark.parametrize(
    "hwm_store_class, input_config, key",
    [
        (
            HorizonHWMStore,
            {
                "hwm_store": {
                    "horizon": {
                        "api_url": "http://some.horizon.url",
                        "auth": {"login": secrets.token_hex(), "password": secrets.token_hex()},
                        "namespace": secrets.token_hex(),
                    },
                },
            },
            "hwm_store",
        ),
    ],
)
@pytest.mark.parametrize("config_constructor", [dict, OmegaConf.create])
def test_hwm_store_unit_detect(hwm_store_class, input_config, config_constructor, key):
    @detect_hwm_store(key)
    def main(config):
        assert isinstance(HWMStoreManager.get_current(), hwm_store_class)

    conf = config_constructor(input_config)
    main(conf)


@pytest.mark.parametrize(
    "input_config",
    [
        {"hwm_store": 1},
        {"hwm_store": "unknown"},
        {"hwm_store": {"unknown": None}},
    ],
)
@pytest.mark.parametrize("config_constructor", [dict, OmegaConf.create])
def test_hwm_store_unit_detect_failure(input_config, config_constructor):
    @detect_hwm_store("hwm_store")
    def main(config):
        pass

    conf = config_constructor(input_config)
    with pytest.raises((KeyError, ValueError)):
        main(conf)

    conf = config_constructor({"nested": input_config})
    with pytest.raises((KeyError, ValueError)):
        main(conf)

    conf = config_constructor({"even": {"more": {"nested": input_config}}})
    with pytest.raises((KeyError, ValueError)):
        main(conf)


@pytest.mark.parametrize(
    "input_config",
    [
        {"hwm_store": {"horizon": 1}},
        {"hwm_store": {"horizon": None}},
        {"hwm_store": {"horizon": "http://some.horizon.url"}},
        {"hwm_store": {"horizon": ["http://some.horizon.url"]}},
        {
            "hwm_store": {
                "horizon": [
                    "positional",
                    "args",
                    "prohibited",
                ],
            },
        },
        {"hwm_store": {"horizon": {}}},
        {"hwm_store": {"horizon": {"unknown": "arg"}}},
    ],
)
@pytest.mark.parametrize("config_constructor", [dict, OmegaConf.create])
def test_hwm_store_unit_wrong_options(input_config, config_constructor):
    @detect_hwm_store("hwm_store")
    def main(config):
        pass

    conf = config_constructor(input_config)

    with pytest.raises((TypeError, ValueError)):
        main(conf)

    conf = config_constructor({"nested": input_config})
    with pytest.raises((TypeError, ValueError)):
        main(conf)

    conf = config_constructor({"even": {"more": {"nested": input_config}}})
    with pytest.raises((TypeError, ValueError)):
        main(conf)
