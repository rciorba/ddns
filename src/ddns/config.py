import ConfigParser
import ddns
import os.path
import logging

_settings = None
logger = logging.getLogger(__name__)


def get_config():
    global _settings
    if _settings is None:
        _config = ConfigParser.ConfigParser()
        default = os.path.join(ddns.__path__[0], "ppusher.conf")
        _config.read(default)
        local_settings = os.getenv("PPUSHER_SETTINGS_OVERRIDE") or os.path.join(
            ddns.__path__[0], "ddns.conf")
        if local_settings:
            _config.read(local_settings)
        _settings = dict((k.upper(), v) for k, v in _config.items("main"))
    return _settings
