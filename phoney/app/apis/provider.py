from inspect import isfunction, getmodule
from types import ModuleType
from typing import Any, Dict, List, Set, Type, cast

from faker import Faker
from faker.providers import BaseProvider
import faker


# Constants for filtering Faker providers
PRIVATE_MEMBERS: Set[str] = {"BaseProvider", "OrderedDict"}
PRIVATE_MEMBER_PREFIXES: Set[str] = {"_", "@", "ALPHA"}
BASE_PROVIDER_METHODS: Set[str] = set(dir(BaseProvider))


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


def get_provider(provider_name: str) -> Type[BaseProvider]:
    """Get a provider class by name."""
    try:
        provider_module = getattr(faker.providers, provider_name)
        return cast(Type[BaseProvider], provider_module.Provider)
    except (AttributeError, ModuleNotFoundError):
        raise ValueError(f"Provider '{provider_name}' not found")


def get_provider_list() -> List[str]:
    """Get a list of all available Faker providers."""
    provider_list: List[str] = []
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


def get_provider_url_map() -> Dict[str, str]:
    """Generate a mapping of provider names to their API URLs."""
    return {provider: f"/provider/{provider}" for provider in get_provider_list()}


def get_generator_list(provider_class: Type[BaseProvider]) -> List[str]:
    """Get a list of all generator methods available in a provider."""
    generator_list: List[str] = []
    
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


def get_provider_metadata() -> Dict[str, Dict[str, Any]]:
    """Get comprehensive metadata about all providers and their generators."""
    metadata: Dict[str, Dict[str, Any]] = {}
    
    for provider_name in get_provider_list():
        try:
            provider_class = get_provider(provider_name)
            generators = get_generator_list(provider_class)
            
            metadata[provider_name] = {
                "name": provider_name,
                "url": f"/provider/{provider_name}",
                "generator_count": len(generators),
                "generators": generators
            }
        except Exception:
            continue
            
    return metadata
