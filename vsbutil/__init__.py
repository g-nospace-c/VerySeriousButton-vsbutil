try:
    from ._version import __version__
except ModuleNotFoundError:
    __version__ = "v0.lol.idk🤷‍♀️"

from . import _vsbutil
from ._vsbutil import *
from . import cli

__all__ = ['cli'] + _vsbutil.__all__
