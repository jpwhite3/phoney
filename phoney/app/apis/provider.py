from types import ModuleType
import faker
from faker.providers import BaseProvider


PRIVATE_MEMBERS = ["BaseProvider", "OrderedDict"]
PRIVATE_MEMBER_PREFIXES = ["_", "@", "ALPHA"]


def is_private_member(member_name: str) -> bool:
    if member_name[0] in PRIVATE_MEMBER_PREFIXES or member_name in PRIVATE_MEMBERS:
        return True
    return False


def is_base_provider_attr(attr_name: str) -> bool:
    if attr_name in dir(BaseProvider):
        return True
    return False


def is_provider(provider_obj) -> bool:
    return isinstance(provider_obj, ModuleType) and "Provider" in dir(provider_obj)


def get_provider(provider_name):
    try:
        provider = getattr(faker.providers, provider_name)
    except AttributeError:
        raise LookupError("Provider not found")
    else:
        return provider.Provider


def get_provider_list():
    provider_list = []
    for provider_name in dir(faker.providers):
        if is_private_member(provider_name):
            continue
        if is_provider(getattr(faker.providers, provider_name)):
            provider_list.append(provider_name)
    return provider_list


def get_provider_url_map():
    return {provider: "/provider/%s" % provider for provider in get_provider_list()}


def get_generator_list(provider_obj):
    generator_list = []
    for attr in dir(provider_obj):
        if is_generator(getattr(provider_obj, attr)):
            generator_list.append(attr)
    return generator_list


def is_generator(generator_obj):
    if hasattr(generator_obj, "__module__"):
        module_name = str(generator_obj.__module__)
        if module_name.startswith("faker.providers."):
            return True
    return False
