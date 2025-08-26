from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator, ConfigDict

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


class SimpleFakeResponse(BaseModel):
    """Simplified response model for the easy-to-use fake data API."""
    generator: str
    data: Union[Any, List[Any]]
    count: int
    locale: str
    seed: Optional[int] = None


# Template System Models

class TemplateField(BaseModel):
    """Individual placeholder definition in a template."""
    generator: str = Field(..., description="Name of the Faker generator to use")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Parameters to pass to the generator")
    array_count: Optional[int] = Field(default=None, description="If specified, generate an array of this size")
    nested_path: Optional[str] = Field(default=None, description="Dot notation path for nested placement")
    
    model_config = ConfigDict(extra='forbid')


class TemplateValidationError(BaseModel):
    """Error information for template validation failures."""
    field: str = Field(..., description="Field name where error occurred")
    generator: str = Field(..., description="Generator that caused the error")
    message: str = Field(..., description="Human-readable error message")
    suggestions: List[str] = Field(default_factory=list, description="Suggested alternative generators")
    error_type: str = Field(default="validation_error", description="Type of error")


class BulkTemplate(BaseModel):
    """Template definition for bulk data generation."""
    template: Dict[str, Any] = Field(..., description="Template structure with placeholders")
    count: int = Field(1, ge=1, le=10000, description="Number of records to generate")
    locale: Optional[str] = Field(default=None, description="Locale for localized data generation")
    seed: Optional[int] = Field(default=None, description="Seed for reproducible results")
    unique: bool = Field(default=False, description="Ensure unique values where possible")
    
    model_config = ConfigDict(extra='forbid')
    
    @model_validator(mode='after')
    def validate_template(self) -> 'BulkTemplate':
        """Basic template structure validation."""
        if not self.template:
            raise ValueError("Template cannot be empty")
        return self


class BulkTemplateRequest(BaseModel):
    """Request model for template processing."""
    template: Dict[str, Any] = Field(..., description="Template structure with {{placeholder}} syntax")
    count: int = Field(1, ge=1, le=10000, description="Number of records to generate")
    locale: Optional[str] = Field(default=None, description="Locale for data generation")
    seed: Optional[int] = Field(default=None, description="Seed for reproducible results")
    format: Literal["json", "csv"] = Field(default="json", description="Output format")
    streaming: bool = Field(default=False, description="Enable streaming for large datasets")
    unique: bool = Field(default=False, description="Attempt to generate unique values")
    
    model_config = ConfigDict(extra='forbid')
    
    @model_validator(mode='after')
    def validate_request(self) -> 'BulkTemplateRequest':
        """Validate request parameters."""
        if not self.template:
            raise ValueError("Template is required")
        
        # Enable streaming automatically for large datasets
        if self.count > 1000 and not self.streaming:
            self.streaming = True
            
        return self


class BulkTemplateResponse(BaseModel):
    """Response model for bulk template generation."""
    template_id: Optional[str] = Field(default=None, description="Unique identifier for this template execution")
    generated_count: int = Field(..., description="Number of records actually generated")
    requested_count: int = Field(..., description="Number of records requested")
    data: Union[List[Dict[str, Any]], str] = Field(..., description="Generated data (JSON array or CSV string)")
    format: str = Field(..., description="Format of the returned data")
    locale: str = Field(..., description="Locale used for generation")
    seed: Optional[int] = Field(default=None, description="Seed used for generation")
    execution_time_ms: Optional[float] = Field(default=None, description="Time taken to generate data")
    warnings: List[str] = Field(default_factory=list, description="Any warnings during generation")
    
    model_config = ConfigDict(extra='forbid')


class TemplateValidationRequest(BaseModel):
    """Request model for template validation."""
    template: Dict[str, Any] = Field(..., description="Template to validate")
    strict: bool = Field(default=False, description="Enable strict validation mode")
    
    model_config = ConfigDict(extra='forbid')


class TemplateValidationResponse(BaseModel):
    """Response model for template validation."""
    valid: bool = Field(..., description="Whether the template is valid")
    errors: List[TemplateValidationError] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    detected_fields: List[TemplateField] = Field(default_factory=list, description="Detected template fields")
    estimated_size: Optional[int] = Field(default=None, description="Estimated output size for count=1")
    
    model_config = ConfigDict(extra='forbid')
