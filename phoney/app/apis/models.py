from enum import Enum
from .provider import get_provider_list

FakeDataProvider = Enum("FakeDataProvider", {x.lower(): x for x in get_provider_list()}, type=str)
