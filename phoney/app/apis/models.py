from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .provider import get_provider_list

# Create enum for available Faker providers
FakeDataProvider = Enum(
    "FakeDataProvider", {x.lower(): x for x in get_provider_list()}, type=str
)


class GeneratorParams(BaseModel):
    """Parameters for a Faker generator method."""

    args: list[Any] = Field(
        default_factory=list, description="Positional arguments for the generator"
    )
    kwargs: dict[str, Any] = Field(
        default_factory=dict, description="Keyword arguments for the generator"
    )

    @model_validator(mode="after")
    def validate_args_types(self) -> "GeneratorParams":
        """Ensure arguments are JSON serializable."""
        return self


class FakerRequest(BaseModel):
    """Request model for generating fake data."""

    provider: FakeDataProvider
    generator: str
    locale: str | None = None
    seed: int | None = None
    unique: bool = False
    count: int = Field(1, ge=1, le=100, description="Number of items to generate")
    params: GeneratorParams | None = None


class FakerResponse(BaseModel):
    """Response model for fake data generation."""

    provider: str
    generator: str
    data: Any | list[Any]
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
    generators: list[str]
    generator_urls: dict[str, str]


class SimpleFakeResponse(BaseModel):
    """Simplified response model for the easy-to-use fake data API."""

    generator: str
    data: Any | list[Any]
    count: int
    locale: str
    seed: int | None = None


# Template System Models


class TemplateField(BaseModel):
    """Individual placeholder definition in a template."""

    generator: str = Field(..., description="Name of the Faker generator to use")
    parameters: dict[str, Any] | None = Field(
        default=None, description="Parameters to pass to the generator"
    )
    array_count: int | None = Field(
        default=None, description="If specified, generate an array of this size"
    )
    nested_path: str | None = Field(
        default=None, description="Dot notation path for nested placement"
    )

    model_config = ConfigDict(extra="forbid")


class TemplateValidationError(BaseModel):
    """Error information for template validation failures."""

    field: str = Field(..., description="Field name where error occurred")
    generator: str = Field(..., description="Generator that caused the error")
    message: str = Field(..., description="Human-readable error message")
    suggestions: list[str] = Field(
        default_factory=list, description="Suggested alternative generators"
    )
    error_type: str = Field(default="validation_error", description="Type of error")


class BulkTemplate(BaseModel):
    """Template definition for bulk data generation."""

    template: dict[str, Any] = Field(
        ..., description="Template structure with placeholders"
    )
    count: int = Field(1, ge=1, le=10000, description="Number of records to generate")
    locale: str | None = Field(
        default=None, description="Locale for localized data generation"
    )
    seed: int | None = Field(default=None, description="Seed for reproducible results")
    unique: bool = Field(
        default=False, description="Ensure unique values where possible"
    )

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_template(self) -> "BulkTemplate":
        """Basic template structure validation."""
        if not self.template:
            raise ValueError("Template cannot be empty")
        return self


class BulkTemplateRequest(BaseModel):
    """Request model for template processing."""

    template: dict[str, Any] = Field(
        ..., description="Template structure with {{placeholder}} syntax"
    )
    count: int = Field(1, ge=1, le=10000, description="Number of records to generate")
    locale: str | None = Field(default=None, description="Locale for data generation")
    seed: int | None = Field(default=None, description="Seed for reproducible results")
    format: Literal["json", "csv"] = Field(default="json", description="Output format")
    streaming: bool = Field(
        default=False, description="Enable streaming for large datasets"
    )
    unique: bool = Field(default=False, description="Attempt to generate unique values")

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_request(self) -> "BulkTemplateRequest":
        """Validate request parameters."""
        if not self.template:
            raise ValueError("Template is required")

        # Enable streaming automatically for large datasets
        if self.count > 1000 and not self.streaming:
            self.streaming = True

        return self


class BulkTemplateResponse(BaseModel):
    """Response model for bulk template generation."""

    template_id: str | None = Field(
        default=None, description="Unique identifier for this template execution"
    )
    generated_count: int = Field(
        ..., description="Number of records actually generated"
    )
    requested_count: int = Field(..., description="Number of records requested")
    data: list[dict[str, Any]] | str = Field(
        ..., description="Generated data (JSON array or CSV string)"
    )
    format: str = Field(..., description="Format of the returned data")
    locale: str = Field(..., description="Locale used for generation")
    seed: int | None = Field(default=None, description="Seed used for generation")
    execution_time_ms: float | None = Field(
        default=None, description="Time taken to generate data"
    )
    warnings: list[str] = Field(
        default_factory=list, description="Any warnings during generation"
    )

    model_config = ConfigDict(extra="forbid")


class TemplateValidationRequest(BaseModel):
    """Request model for template validation."""

    template: dict[str, Any] = Field(..., description="Template to validate")
    strict: bool = Field(default=False, description="Enable strict validation mode")

    model_config = ConfigDict(extra="forbid")


class TemplateValidationResponse(BaseModel):
    """Response model for template validation."""

    valid: bool = Field(..., description="Whether the template is valid")
    errors: list[TemplateValidationError] = Field(
        default_factory=list, description="Validation errors"
    )
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
    detected_fields: list[TemplateField] = Field(
        default_factory=list, description="Detected template fields"
    )
    estimated_size: int | None = Field(
        default=None, description="Estimated output size for count=1"
    )

    model_config = ConfigDict(extra="forbid")
