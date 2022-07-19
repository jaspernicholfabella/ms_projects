import logging
from ._data import Data
from ._decorator import Decorator
from ._files import Files
from ._html import HTML
from ._json import JSON
from ._parse import Parse
from ._strings import Strings

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


strings = Strings(logger)
files = Files(logger)
html = HTML(logger)
json = JSON(logger)
parse = Parse(logger)
decorator = Decorator(logger)
data = Data(logger)
