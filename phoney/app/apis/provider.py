from inspect import getmodule, isfunction
from types import ModuleType
from typing import Any, cast

import faker
from faker import Faker
from faker.providers import BaseProvider

# Constants for filtering Faker providers
PRIVATE_MEMBERS: set[str] = {"BaseProvider", "OrderedDict"}
PRIVATE_MEMBER_PREFIXES: set[str] = {"_", "@", "ALPHA"}
BASE_PROVIDER_METHODS: set[str] = set(dir(BaseProvider))


def is_private_member(member_name: str) -> bool:
    """Check if a member name should be considered private."""
    if not member_name:
        return True
    if member_name[0] in PRIVATE_MEMBER_PREFIXES or member_name in PRIVATE_MEMBERS:
        return True
    return False


def is_base_provider_attr(attr_name: str) -> bool:
    """Check if an attribute is from the BaseProvider class."""
    return attr_name in BASE_PROVIDER_METHODS


def is_provider(provider_obj: Any) -> bool:
    """Determine if an object is a valid Faker provider module."""
    return isinstance(provider_obj, ModuleType) and hasattr(provider_obj, "Provider")


def is_generator(obj: Any) -> bool:
    """Check if an object is a Faker generator function."""
    if not isfunction(obj):
        return False

    module = getmodule(obj)
    if not module:
        return False

    module_name = module.__name__
    return module_name.startswith("faker.providers.")


def get_provider(provider_name: str) -> type[BaseProvider]:
    """Get a provider class by name."""
    try:
        provider_module = getattr(faker.providers, provider_name)
        return cast(type[BaseProvider], provider_module.Provider)
    except (AttributeError, ModuleNotFoundError):
        raise ValueError(f"Provider '{provider_name}' not found")


def get_provider_list() -> list[str]:
    """Get a list of all available Faker providers."""
    provider_list: list[str] = []
    for provider_name in dir(faker.providers):
        if is_private_member(provider_name):
            continue

        try:
            provider_obj = getattr(faker.providers, provider_name)
            if is_provider(provider_obj):
                provider_list.append(provider_name)
        except (AttributeError, ImportError):
            continue

    return provider_list


def get_provider_url_map() -> dict[str, str]:
    """Generate a mapping of provider names to their API URLs."""
    return {provider: f"/provider/{provider}" for provider in get_provider_list()}


def get_generator_list(provider_class: type[BaseProvider]) -> list[str]:
    """Get a list of all generator methods available in a provider."""
    generator_list: list[str] = []

    # Create an instance to inspect its methods
    fake = Faker()
    provider_instance = provider_class(fake)

    for attr_name in dir(provider_instance):
        # Skip private and internal methods
        if is_private_member(attr_name) or is_base_provider_attr(attr_name):
            continue

        try:
            attr = getattr(provider_instance, attr_name)
            if isfunction(attr) or callable(attr):
                generator_list.append(attr_name)
        except (AttributeError, ImportError):
            continue

    return generator_list


def get_provider_metadata() -> dict[str, dict[str, Any]]:
    """Get comprehensive metadata about all providers and their generators."""
    metadata: dict[str, dict[str, Any]] = {}

    for provider_name in get_provider_list():
        try:
            provider_class = get_provider(provider_name)
            generators = get_generator_list(provider_class)

            metadata[provider_name] = {
                "name": provider_name,
                "url": f"/provider/{provider_name}",
                "generator_count": len(generators),
                "generators": generators,
            }
        except Exception:
            continue

    return metadata


def find_generator(fake_instance: Faker, requested_generator: str) -> str | None:
    """Smart generator finder that maps common requests to actual Faker methods.

    This function helps beginners by accepting intuitive names and mapping them
    to the actual Faker generator methods.
    """

    # Direct match - if the generator exists as-is, use it
    if hasattr(fake_instance, requested_generator):
        return requested_generator

    # Common mappings for beginner-friendly names
    generator_mappings = {
        # Person-related
        "name": "name",
        "first_name": "first_name",
        "last_name": "last_name",
        "full_name": "name",
        "person": "name",
        "username": "user_name",
        "user": "user_name",
        # Contact info
        "email": "email",
        "mail": "email",
        "phone": "phone_number",
        "telephone": "phone_number",
        "mobile": "phone_number",
        # Address
        "address": "address",
        "street": "street_address",
        "city": "city",
        "state": "state",
        "country": "country",
        "zip": "zipcode",
        "postal": "postcode",
        "zipcode": "zipcode",
        # Internet
        "url": "url",
        "website": "url",
        "domain": "domain_name",
        "ip": "ipv4",
        "ipv4": "ipv4",
        "ipv6": "ipv6",
        # Text
        "text": "text",
        "paragraph": "paragraph",
        "sentence": "sentence",
        "word": "word",
        "words": "words",
        # Date/Time
        "date": "date",
        "time": "time",
        "datetime": "date_time",
        "timestamp": "unix_time",
        # Numbers
        "number": "random_int",
        "integer": "random_int",
        "float": "pyfloat",
        "decimal": "pydecimal",
        # Company/Job
        "company": "company",
        "job": "job",
        "profession": "job",
        # Colors
        "color": "color_name",
        "hex_color": "hex_color",
        # UUID
        "uuid": "uuid4",
        "guid": "uuid4",
        # Boolean
        "boolean": "pybool",
        "bool": "pybool",
    }

    # Check if we have a mapping for the requested generator
    mapped_generator = generator_mappings.get(requested_generator.lower())
    if mapped_generator and hasattr(fake_instance, mapped_generator):
        return mapped_generator

    # Fuzzy matching - look for partial matches in available methods
    available_methods = []
    for attr in dir(fake_instance):
        if not attr.startswith("_"):
            try:
                attr_obj = getattr(fake_instance, attr)
                if callable(attr_obj):
                    available_methods.append(attr)
            except (AttributeError, TypeError):
                # Skip attributes that can't be accessed or are deprecated
                continue

    # Try exact substring match first
    for method in available_methods:
        if requested_generator.lower() in method.lower():
            return method

    # Try reverse substring match
    for method in available_methods:
        if method.lower() in requested_generator.lower():
            return method

    return None
