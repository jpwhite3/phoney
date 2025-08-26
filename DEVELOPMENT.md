# Phoney API Development Guide

This document provides comprehensive information about developing and contributing to the Phoney API project.

## Quick Start

```bash
# Install dependencies
make install-dev

# Run all checks (linting + tests with coverage)
make check

# Start development server
make serve

# View API documentation
open http://localhost:8000/docs
```

## Development Commands

The project includes a comprehensive Makefile that mirrors all CI/CD pipeline stages for faster local feedback. Run `make help` to see all available commands.

### Key Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands with descriptions |
| `make install-dev` | Install all development dependencies |
| `make check` | Quick check: run linting and tests with coverage |
| `make ci` | Run complete CI/CD pipeline simulation |
| `make serve` | Start development server with auto-reload |
| `make format` | Auto-format code with black and isort |

### CI/CD Pipeline Simulation

Run the exact same checks that happen in GitHub Actions:

```bash
# Individual pipeline stages
make pipeline-lint      # Simulate lint stage
make pipeline-test      # Simulate test stage  
make pipeline-coverage  # Simulate coverage stage

# Complete pipeline simulation
make pipeline-full      # Run all stages
```

### Code Quality

```bash
# Linting (mirrors CI exactly)
make lint-ruff          # Ruff linting
make lint-mypy          # Type checking
make lint-ci            # All linting checks

# Formatting
make format             # Auto-format with black and isort
make format-check       # Check formatting without changes
```

### Testing

```bash
# Unit testing
make test-unit          # Run unit tests only
make test-integration   # Run integration tests
make test-coverage      # Tests with coverage reporting
make test-coverage-html # Generate HTML coverage report
make test-ci            # Full CI test suite
```

### Development Server

```bash
make serve              # Standard development server
make serve-dev          # Development server with debug logging
make serve-prod         # Production server configuration
```

### Docker

```bash
make docker-build       # Build Docker image
make docker-run         # Build and run container
make docker-test        # Run tests in container
```

## Project Structure

```
phoney/
├── phoney/app/         # Main application code
│   ├── apis/          # API logic and models
│   ├── core/          # Core functionality (auth, config, security)
│   ├── routes/        # API route definitions
│   └── main.py        # FastAPI application setup
├── tests/             # Test suite
├── examples/          # API usage examples
├── aws-infrastructure/ # AWS deployment configs
└── Makefile          # Development commands
```

## Configuration

The application uses environment variables for configuration. See `.env` files or `phoney/app/core/config.py` for available settings.

### Key Settings

- `ENV_STATE`: Environment (dev/test/prod)
- `SECRET_KEY`: JWT signing key (required, min 32 chars)
- `API_USERNAME`/`API_PASSWORD_HASH`: API authentication
- `RATE_LIMIT_PER_MINUTE`: Request rate limiting
- `LOG_LEVEL`: Logging verbosity

## Python Version Support

The project supports Python 3.10-3.13. Use `make ci` to test your changes across different Python versions in CI.

## Code Style

- **Formatting**: Black with 88 character line length
- **Import sorting**: isort with black profile
- **Linting**: Ruff with security checks
- **Type checking**: mypy with strict settings

Run `make format` to auto-format your code, then `make lint-ci` to check for issues.

## Testing Strategy

- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: Test API endpoints and full workflows
- **Performance Tests**: Ensure response times meet requirements
- **Coverage**: Minimum 75% required, target 90%

## Contributing

1. **Setup**: Run `make install-dev` to set up your development environment
2. **Development**: Make your changes and test locally with `make check`
3. **Testing**: Ensure all tests pass with `make test-ci`
4. **Pipeline**: Run `make ci` to simulate the full CI/CD pipeline
5. **Format**: Run `make format` before committing
6. **Submit**: Create a pull request

## Deployment

The project supports multiple deployment options:

- **Local Development**: `make serve`
- **Docker**: `make docker-run`
- **AWS Lambda**: Automated via GitHub Actions
- **Production**: `make build` creates distribution packages

## Troubleshooting

### Common Issues

**Import sorting conflicts**: Run `make format` to fix import organization.

**Test failures**: Check test output and run `make test-unit` to isolate issues.

**Coverage too low**: Run `make test-coverage-html` to see coverage report.

**Docker issues**: Run `make clean-docker` to clean up containers and images.

### Environment Issues

**Python version**: Ensure you're using Python 3.10-3.13.

**Dependencies**: Run `make install-dev` to refresh dependencies.

**Environment variables**: Check `.env` file exists with required settings.

## Performance

The API is designed to handle:
- Template generation: < 5 seconds for complex templates
- Simple requests: < 100ms response time
- Rate limiting: Configurable per-minute limits
- Concurrent requests: Async FastAPI architecture

Run performance tests with `make test` to verify your changes don't impact performance.

## Security

The project includes comprehensive security measures:
- JWT authentication for protected endpoints
- Rate limiting to prevent abuse
- Security headers for XSS/CSRF protection
- Input validation with Pydantic models
- Dependency security scanning in CI

Security issues are checked automatically via `make lint-ci`.