"""
Template Engine for Phoney Bulk Template System

This module handles parsing and processing of template placeholders,
generator resolution, and data generation from templates.
"""

import re
import json
from typing import Any, Dict, List, Optional, Tuple, Union
from faker import Faker

from .provider import find_generator
from .models import TemplateField, TemplateValidationError


class TemplateParser:
    """Parser for template placeholders with parameter support."""
    
    # Regex patterns for different placeholder formats
    SIMPLE_PLACEHOLDER = re.compile(r'\{\{([^}:]+)\}\}')
    PARAM_PLACEHOLDER = re.compile(r'\{\{([^}:]+):([^}]+)\}\}')
    ARRAY_PLACEHOLDER = re.compile(r'\{\{\[([^}:]+)\]:([^}]+)\}\}')
    NESTED_PLACEHOLDER = re.compile(r'\{\{([^}]+\.+[^}]+)\}\}')
    
    @classmethod
    def parse_parameters(cls, param_string: str) -> Dict[str, Any]:
        """Parse parameter string like 'min=1,max=100,locale=en_US' into dict."""
        if not param_string:
            return {}
        
        params = {}
        # Split on comma but handle quoted values
        param_pairs = re.findall(r'(\w+)=([^,]+)', param_string)
        
        for key, value in param_pairs:
            # Try to parse as different types
            value = value.strip()
            
            # Boolean values
            if value.lower() in ('true', 'false'):
                params[key] = value.lower() == 'true'
            # Integer values
            elif value.isdigit():
                params[key] = int(value)
            # Float values
            elif re.match(r'^\d+\.\d+$', value):
                params[key] = float(value)
            # String values (remove quotes if present)
            else:
                params[key] = value.strip('\'"')
        
        return params
    
    @classmethod
    def extract_placeholders(cls, template: Any, path: str = '') -> List[TemplateField]:
        """Extract all placeholders from a template structure."""
        fields = []
        
        if isinstance(template, dict):
            for key, value in template.items():
                current_path = f"{path}.{key}" if path else key
                fields.extend(cls.extract_placeholders(value, current_path))
        
        elif isinstance(template, list):
            for i, item in enumerate(template):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                fields.extend(cls.extract_placeholders(item, current_path))
        
        elif isinstance(template, str):
            fields.extend(cls._parse_string_placeholders(template, path))
        
        return fields
    
    @classmethod
    def _parse_string_placeholders(cls, text: str, path: str) -> List[TemplateField]:
        """Parse placeholders from a string value."""
        fields = []
        
        # Check for array placeholders first ({{[generator]:count=5}})
        for match in cls.ARRAY_PLACEHOLDER.finditer(text):
            generator = match.group(1).strip()
            param_string = match.group(2).strip()
            params = cls.parse_parameters(param_string)
            
            # Extract count from parameters
            array_count = params.pop('count', None)
            if array_count is None:
                array_count = 1  # Default array size
            
            fields.append(TemplateField(
                generator=generator,
                parameters=params if params else None,
                array_count=array_count,
                nested_path=path
            ))
        
        # Check for parameterized placeholders ({{generator:param=value}})
        for match in cls.PARAM_PLACEHOLDER.finditer(text):
            generator = match.group(1).strip()
            param_string = match.group(2).strip()
            params = cls.parse_parameters(param_string)
            
            fields.append(TemplateField(
                generator=generator,
                parameters=params if params else None,
                nested_path=path
            ))
        
        # Check for simple placeholders ({{generator}})
        for match in cls.SIMPLE_PLACEHOLDER.finditer(text):
            full_match = match.group(0)
            generator = match.group(1).strip()
            
            # Skip if this was already matched by other patterns
            if any(field.generator == generator and field.nested_path == path for field in fields):
                continue
            
            # Handle nested generators (user.name, contact.email)
            if '.' in generator:
                # This is a nested reference, parse it
                parts = generator.split('.')
                base_generator = parts[-1]  # Use the last part as generator
                fields.append(TemplateField(
                    generator=base_generator,
                    nested_path=path
                ))
            else:
                fields.append(TemplateField(
                    generator=generator,
                    nested_path=path
                ))
        
        return fields


class TemplateValidator:
    """Validates template structures and placeholders."""
    
    def __init__(self, faker_instance: Optional[Faker] = None):
        self.faker = faker_instance or Faker()
    
    def validate_template(self, template: Dict[str, Any], strict: bool = False) -> Tuple[bool, List[TemplateValidationError], List[str]]:
        """
        Validate a template structure.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        try:
            import warnings as warn_module
            # Temporarily suppress deprecation warnings during validation
            with warn_module.catch_warnings():
                warn_module.filterwarnings("ignore", category=DeprecationWarning)
                
                # Extract all placeholders
                fields = TemplateParser.extract_placeholders(template)
                
                if not fields:
                    errors.append(TemplateValidationError(
                        field="template",
                        generator="none",
                        message="No placeholders found in template",
                        error_type="no_placeholders"
                    ))
                
                # Validate each field
                for field in fields:
                    field_errors, field_warnings = self._validate_field(field, strict)
                    errors.extend(field_errors)
                    warnings.extend(field_warnings)
            
        except Exception as e:
            # Skip deprecation warnings as errors
            if "deprecated" not in str(e).lower():
                errors.append(TemplateValidationError(
                    field="template",
                    generator="unknown",
                    message=f"Template parsing error: {str(e)}",
                    error_type="parsing_error"
                ))
        
        return len(errors) == 0, errors, warnings
    
    def _validate_field(self, field: TemplateField, strict: bool) -> Tuple[List[TemplateValidationError], List[str]]:
        """Validate a single template field."""
        errors = []
        warnings = []
        
        # Check if generator exists
        actual_generator = find_generator(self.faker, field.generator)
        
        if not actual_generator:
            # Get suggestions for similar generators
            available_generators = []
            for attr in dir(self.faker):
                if not attr.startswith('_'):
                    try:
                        attr_obj = getattr(self.faker, attr, None)
                        if callable(attr_obj):
                            available_generators.append(attr)
                    except (AttributeError, TypeError):
                        # Skip attributes that can't be accessed or are deprecated
                        continue
            
            suggestions = []
            field_lower = field.generator.lower()
            
            # Find close matches
            for gen in available_generators:
                if field_lower in gen.lower() or gen.lower() in field_lower:
                    suggestions.append(gen)
            
            errors.append(TemplateValidationError(
                field=field.nested_path or "unknown",
                generator=field.generator,
                message=f"Generator '{field.generator}' not found",
                suggestions=suggestions[:5],  # Limit to 5 suggestions
                error_type="generator_not_found"
            ))
        else:
            # Validate parameters if present
            if field.parameters:
                param_errors, param_warnings = self._validate_parameters(
                    actual_generator, field.parameters, field.nested_path
                )
                errors.extend(param_errors)
                warnings.extend(param_warnings)
        
        # Validate array count
        if field.array_count is not None:
            if field.array_count < 1:
                errors.append(TemplateValidationError(
                    field=field.nested_path or "unknown",
                    generator=field.generator,
                    message=f"Array count must be positive, got {field.array_count}",
                    error_type="invalid_array_count"
                ))
            elif field.array_count > 1000:
                warnings.append(f"Large array count ({field.array_count}) may impact performance")
        
        return errors, warnings
    
    def _validate_parameters(self, generator_name: str, parameters: Dict[str, Any], field_path: str) -> Tuple[List[TemplateValidationError], List[str]]:
        """Validate parameters for a specific generator."""
        errors = []
        warnings = []
        
        # Try to call the generator with the parameters to validate
        try:
            generator_func = getattr(self.faker, generator_name)
            
            # Extract args and kwargs from parameters, excluding 'count' which is for arrays
            args = parameters.get('args', [])
            kwargs = {k: v for k, v in parameters.items() if k not in ['args', 'count']}
            
            # Test call (don't actually use the result)
            # Suppress warnings during validation
            import warnings as warn_module
            with warn_module.catch_warnings():
                warn_module.filterwarnings("ignore", category=DeprecationWarning)
                generator_func(*args, **kwargs)
            
        except TypeError as e:
            error_msg = str(e)
            if "unexpected keyword argument" in error_msg:
                # Extract the problematic parameter
                param_match = re.search(r"'(\w+)'", error_msg)
                param_name = param_match.group(1) if param_match else "unknown"
                errors.append(TemplateValidationError(
                    field=field_path,
                    generator=generator_name,
                    message=f"Invalid parameter '{param_name}' for generator '{generator_name}'",
                    error_type="invalid_parameter"
                ))
            else:
                errors.append(TemplateValidationError(
                    field=field_path,
                    generator=generator_name,
                    message=f"Parameter error: {error_msg}",
                    error_type="parameter_error"
                ))
        
        except Exception as e:
            warnings.append(f"Could not validate parameters for {generator_name}: {str(e)}")
        
        return errors, warnings


class TemplateProcessor:
    """Processes templates and generates data."""
    
    def __init__(self, locale: Optional[str] = None, seed: Optional[int] = None):
        self.faker = Faker(locale=locale) if locale else Faker()
        if seed is not None:
            self.faker.seed_instance(seed)
        self.locale = locale or 'en_US'
        self.seed = seed
    
    def process_template(self, template: Dict[str, Any], count: int = 1, unique: bool = False) -> List[Dict[str, Any]]:
        """Process a template and generate the requested number of records."""
        if unique:
            # Clear any existing unique constraints
            try:
                self.faker.unique.clear()
            except AttributeError:
                # Unique functionality might not be available
                pass
        
        results = []
        for _ in range(count):
            try:
                result = self._process_template_item(template)
                results.append(result)
            except Exception as e:
                # For failed generation, continue with warning
                # In production, you might want to log this
                continue
        
        return results
    
    def _process_template_item(self, item: Any) -> Any:
        """Process a single template item (recursive)."""
        if isinstance(item, dict):
            return {key: self._process_template_item(value) for key, value in item.items()}
        
        elif isinstance(item, list):
            return [self._process_template_item(list_item) for list_item in item]
        
        elif isinstance(item, str):
            return self._process_string_placeholders(item)
        
        else:
            return item
    
    def _process_string_placeholders(self, text: str) -> Any:
        """Process placeholders in a string value."""
        result = text
        
        # Process array placeholders first
        for match in TemplateParser.ARRAY_PLACEHOLDER.finditer(text):
            placeholder = match.group(0)
            generator = match.group(1).strip()
            param_string = match.group(2).strip()
            params = TemplateParser.parse_parameters(param_string)
            
            array_count = params.pop('count', 1)
            generated_array = self._generate_array(generator, array_count, params)
            
            # If the entire string is just this placeholder, return the array
            if result.strip() == placeholder:
                return generated_array
            else:
                # Replace with JSON representation
                result = result.replace(placeholder, json.dumps(generated_array))
        
        # Process parameterized placeholders
        for match in TemplateParser.PARAM_PLACEHOLDER.finditer(text):
            placeholder = match.group(0)
            generator = match.group(1).strip()
            param_string = match.group(2).strip()
            params = TemplateParser.parse_parameters(param_string)
            
            generated_value = self._generate_value(generator, params)
            
            # If the entire string is just this placeholder, return the raw value
            if result.strip() == placeholder:
                return generated_value
            else:
                # Replace with string representation
                result = result.replace(placeholder, str(generated_value))
        
        # Process simple placeholders
        for match in TemplateParser.SIMPLE_PLACEHOLDER.finditer(result):
            placeholder = match.group(0)
            generator = match.group(1).strip()
            
            # Handle nested generators
            if '.' in generator:
                generator = generator.split('.')[-1]
            
            generated_value = self._generate_value(generator)
            
            # If the entire string is just this placeholder, return the raw value
            if result.strip() == placeholder:
                return generated_value
            else:
                # Replace with string representation
                result = result.replace(placeholder, str(generated_value))
        
        return result
    
    def _generate_value(self, generator: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Generate a single value using the specified generator."""
        # Find the actual generator name
        actual_generator = find_generator(self.faker, generator)
        if not actual_generator:
            raise ValueError(f"Generator '{generator}' not found")
        
        generator_func = getattr(self.faker, actual_generator)
        
        if params:
            args = params.get('args', [])
            kwargs = {k: v for k, v in params.items() if k != 'args'}
            return generator_func(*args, **kwargs)
        else:
            return generator_func()
    
    def _generate_array(self, generator: str, count: int, params: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Generate an array of values."""
        return [self._generate_value(generator, params) for _ in range(count)]


class TemplateEngine:
    """Main template engine interface."""
    
    def __init__(self):
        self.parser = TemplateParser()
    
    def validate_template(self, template: Dict[str, Any], strict: bool = False) -> Tuple[bool, List[TemplateValidationError], List[str]]:
        """Validate a template."""
        validator = TemplateValidator()
        return validator.validate_template(template, strict)
    
    def process_template(self, template: Dict[str, Any], count: int = 1, 
                        locale: Optional[str] = None, seed: Optional[int] = None,
                        unique: bool = False) -> List[Dict[str, Any]]:
        """Process a template and generate data."""
        processor = TemplateProcessor(locale=locale, seed=seed)
        return processor.process_template(template, count, unique)
    
    def extract_placeholders(self, template: Dict[str, Any]) -> List[TemplateField]:
        """Extract all placeholders from a template."""
        return self.parser.extract_placeholders(template)