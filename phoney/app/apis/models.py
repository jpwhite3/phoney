from enum import Enum

from .provider import get_provider_list


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

FakeDataProvider = Enum('FakeDataProvider', {x.lower():x for x in get_provider_list()}, type=str)
