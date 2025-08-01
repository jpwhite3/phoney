from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator

from .provider import get_provider_list

# Create enum for available Faker providers
FakeDataProvider = Enum("FakeDataProvider", {x.lower(): x for x in get_provider_list()}, type=str)


class GeneratorParams(BaseModel):
    """Parameters for a Faker generator method."""
    args: List[Any] = Field(default_factory=list, description="Positional arguments for the generator")
    kwargs: Dict[str, Any] = Field(default_factory=dict, description="Keyword arguments for the generator")

    @model_validator(mode='after')
    def validate_args_types(self) -> 'GeneratorParams':
        """Ensure arguments are JSON serializable."""
        return self


class FakerRequest(BaseModel):
    """Request model for generating fake data."""
    provider: FakeDataProvider
    generator: str
    locale: Optional[str] = None
    seed: Optional[int] = None
    unique: bool = False
    count: int = Field(1, ge=1, le=100, description="Number of items to generate")
    params: Optional[GeneratorParams] = None


class FakerResponse(BaseModel):
    """Response model for fake data generation."""
    provider: str
    generator: str
    data: Union[Any, List[Any]]
    count: int


class ProviderInfo(BaseModel):
    """Provider information model."""
    name: str
    url: str
    generator_count: int = 0


class GeneratorInfo(BaseModel):
    """Generator information model."""
    name: str
    url: str


class ProviderDetail(BaseModel):
    """Detailed information about a provider."""
    provider: str
    generators: List[str]
    generator_urls: Dict[str, str]
