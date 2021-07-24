from types import ModuleType
import faker
from faker.providers import BaseProvider

# fake = Faker()

PRIVATE_MEMBERS = ["BaseProvider", "OrderedDict"]
PRIVATE_MEMBER_PREFIXES = ["_", "@"]


def is_private_member(member_name: str) -> bool:
    if member_name[0] in PRIVATE_MEMBER_PREFIXES or member_name in PRIVATE_MEMBERS:
        return True
    return False


def is_base_provider_attr(attr_name: str) -> bool:
    if attr_name in dir(BaseProvider):
        return True
    return False


def is_provider(provider_obj) -> bool:
    return isinstance(provider_obj, ModuleType) and 'Provider' in dir(provider_obj)


def get_provider(provider_name):
    provider = getattr(faker.providers, provider_name)
    if is_provider(provider):
        return provider.Provider
    raise LookupError("Provider not found")


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
    return dir(provider_obj)


