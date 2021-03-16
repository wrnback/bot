from json import load
from logging import (
    getLogger, StreamHandler, Formatter, ERROR, DEBUG
)

from .exceptions import ConfigUpploadError


class Base:

    def __init__(self, *, module_path=__name__, debug=False):
        self._upload_config()
        self._get_logger(module_path, debug)

    @classmethod
    def _upload_config(cls):
        try:
            with open("config.json", 'r') as f:
                cls.config = load(f)
        except Exception as e:
            raise ConfigUpploadError(f"Config loading error - {e}")

    def _get_logger(self, module_path, debug):
        self.logger = getLogger(module_path)
        self.logger.setLevel(DEBUG if debug else ERROR)
        handler = StreamHandler()
        handler.setFormatter(Formatter(
            "[%(asctime)s] %(levelname)s -> (%(name)s.%(funcName)s:%(lineno)d)" + \
            " msg: %(message)s"
        ))
        self.logger.addHandler(handler)