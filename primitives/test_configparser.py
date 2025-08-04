from typing import Final
import pytest
import tempfile
import configparser
# [DEFAULT.secrets]
# public-key = "faksdjgqp8h23r"
# [DEFAULT.button]
# lablel = "test-1"


TOML_CONFIG_CONTENT: Final = """
[DEFAULT]
label = "test"

[[block]]
id = "b-01"

[[block]]
id = "b-02"
"""


@pytest.fixture(autouse=True)
def config_file():
    with tempfile.NamedTemporaryFile() as f:
        f.write(TOML_CONFIG_CONTENT.encode("utf-8"))
        f.flush()
        yield f


def test_load_toml_config(config_file: tempfile.NamedTemporaryFile):
    config = configparser.ConfigParser()
    # config.read(config_file.name)

    print(config["DEFAULT"].items().__dir__())
    # assert config.get("block", "secrets") == "faksdjgqp8h23r"

    # print(config.sections())
    # print(config.get("main", "NOT"))
