import faker
from faker.providers import BaseProvider

fake = faker.Faker()


def is_private_member(member_name):
    if member_name[0] in ["_", "@"] or member_name in ("BaseProvider", "OrderedDict"):
        return True
    return False


def is_base_provider_attr(attr_name):
    if attr_name in dir(BaseProvider):
        return True
    return False


def get_provider_list():
    return [x for x in dir(faker.providers) if not is_private_member(x)]
