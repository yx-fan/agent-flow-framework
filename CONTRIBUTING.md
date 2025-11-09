# Contributing to MCP Framework

Thank you for your interest in contributing to MCP Framework! 🎉

MCP Framework is a **framework** for building multi-agent systems. We welcome contributions that improve the framework itself, not domain-specific agents, nodes, or tools (those should be built by framework users).

## 🤝 How to Contribute

### Reporting Issues

If you find a bug or have a feature request for the framework, please open an issue on GitHub with:
- A clear description of the problem or feature
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Code examples if applicable

### Submitting Pull Requests

1. **Fork the repository** and clone it locally
2. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the code style guidelines below
4. **Test your changes** to ensure they work correctly
5. **Commit your changes** with clear, descriptive messages
6. **Push to your fork** and open a Pull Request

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Add docstrings to classes and functions
- Keep functions focused and modular
- Write clear, descriptive variable and function names

### Project Structure

- `core/` - Base abstractions and foundational components (BaseAgent, BaseNode, BaseTool, Registry, Config, etc.)
- `orchestrator/` - LangGraph orchestration logic (LangGraphBuilder, AgentRouter, StateManager, etc.)
- `providers/` - LLM provider implementations (AzureOpenAI, etc.)
- `memory/` - Memory interface and implementations (Redis, Vector, etc.)
- `api/` - FastAPI endpoints and controllers
- `agents/`, `nodes/`, `tools/`, `data/` - Example implementations (for reference only)

## 🎯 Framework Contribution Areas

We welcome contributions that improve the **framework itself**:

### Core Framework Components

- **Orchestrator Improvements**: Enhance `LangGraphBuilder`, `AgentRouter`, `StateManager`, or `OrchestratorImpl`
- **Registry System**: Improve the registration and discovery mechanism for agents, nodes, and tools
- **Base Abstractions**: Enhance `BaseAgent`, `BaseNode`, `BaseTool` with new capabilities or better error handling
- **Configuration System**: Improve `core/config.py` with better validation, type safety, or new options
- **Exception Handling**: Improve error handling and exception hierarchy in `core/exceptions.py`
- **Logging System**: Enhance the logging infrastructure in `core/logger.py`

### Provider Support

- **New LLM Providers**: Add support for other LLM providers (OpenAI, Anthropic, Google, etc.) in `providers/`
- **Provider Abstraction**: Improve `BaseLLMProvider` interface or add new provider capabilities
- **Provider Configuration**: Enhance provider configuration and initialization

### Memory & State Management

- **Memory Backends**: Add new memory implementations (PostgreSQL, MongoDB, etc.) in `memory/`
- **Memory Interface**: Enhance `MemoryInterface` with new capabilities
- **State Management**: Improve state persistence, caching, or session management
- **Vector Memory**: Complete or improve vector memory implementation

### API & Integration

- **API Endpoints**: Add new framework-level API endpoints in `api/`
- **Middleware**: Add useful middleware for the FastAPI application
- **Request/Response Handling**: Improve request validation or response formatting

### Documentation & Developer Experience

- **Framework Documentation**: Improve README, add architecture docs, or API documentation
- **Code Examples**: Add examples showing how to use framework features (not domain-specific agents)
- **Type Hints**: Improve type annotations throughout the codebase
- **Error Messages**: Make error messages more helpful and actionable

### Testing & Quality

- **Unit Tests**: Add tests for core framework components
- **Integration Tests**: Add tests for orchestrator, providers, memory, etc.
- **Test Infrastructure**: Set up testing framework and CI/CD
- **Code Quality**: Add linting, formatting, or static analysis

### Performance & Scalability

- **Performance Optimization**: Optimize graph execution, memory usage, or API response times
- **Caching**: Add caching mechanisms for workflows, configurations, or LLM responses
- **Async Improvements**: Enhance async/await patterns for better concurrency
- **Resource Management**: Improve connection pooling, resource cleanup, etc.

## ❌ What NOT to Contribute

Please **do not** submit PRs for:
- Domain-specific agents (e.g., `FinanceAgent`, `EducationAgent`) - these should be built by framework users
- Domain-specific nodes (e.g., `PaymentNode`, `GradeNode`) - these are application-specific
- Domain-specific tools (e.g., `WeatherTool`, `StockTool`) - these belong in user projects
- Domain-specific workflows in `data/` - the `hello` example is sufficient

These are **application-level** concerns that should be built on top of the framework, not within it.

## 📝 Commit Messages

Use clear, descriptive commit messages:
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Be specific about what changed
- Reference issue numbers if applicable

Examples:
```
Add support for OpenAI provider in framework
Fix Redis connection error handling in memory layer
Update LangGraphBuilder to support conditional edges
Improve error messages in BaseAgent
Add type hints to orchestrator components
```

## 🧪 Testing

While we don't have formal tests yet, please:
- Test your changes manually with the existing `hello` example
- Ensure existing functionality still works
- Test edge cases and error handling
- Consider adding tests if you're adding new framework features

## 📚 Documentation

- Update README.md if you add new framework features
- Add docstrings to new classes and functions
- Update architecture documentation if the framework structure changes
- Add code examples showing how to use new framework features

## ❓ Questions?

Feel free to open an issue for questions or discussions about contributing to the framework.

Thank you for contributing to MCP Framework! 🚀
