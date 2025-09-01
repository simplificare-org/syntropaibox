# SyntropAIBox - Core MCP Abstraction Library

**The foundational library powering the [SyntropAI MCP Ecosystem](https://github.com/paihari/documentation-syntropai)**

[![PyPI version](https://img.shields.io/badge/PyPI-syntropaibox-blue)](https://test.pypi.org/project/syntropaibox/)
[![Python Versions](https://img.shields.io/badge/Python-3.10%2B-blue)](https://test.pypi.org/project/syntropaibox/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

SyntropAIBox is the core abstraction library that enables secure, unified access to cloud services and external APIs through Model Context Protocol (MCP) servers. It provides the foundation for creating provider-agnostic, secure, and extensible MCP implementations.

## 🚀 Key Features

### 🔒 Security-First Architecture
- **AST-Based Validation**: Prevents code injection through abstract syntax tree analysis
- **Sandboxed Execution**: Controlled runtime environment with timeout protection
- **Whitelisted Imports**: Only approved modules and functions are accessible
- **Safe Builtins**: Restricted built-in function access

### 🌐 Provider-Agnostic Abstractions
- **BaseSession**: Unified authentication pattern across cloud providers
- **BaseQuerier**: Secure code execution engine with provider flexibility
- **Dynamic Schema Generation**: Runtime API documentation creation
- **Extensible Architecture**: Easy addition of new cloud providers

### ⚡ Production-Ready Features
- **Timeout Protection**: Prevents runaway code execution
- **Error Handling**: Comprehensive exception management with JSON serialization
- **Logging Integration**: Built-in logging for debugging and monitoring
- **Type Safety**: Full Pydantic integration for data validation

## 🏗️ Core Architecture

```
User Code → AST Parser → Security Validation → Safe Execution → JSON Response
     ↓           ↓              ↓                    ↓              ↓
Input Validation → Whitelist Check → Namespace Setup → SDK Call → Serialization
```

### Key Components

#### BaseQuerier
The core query execution engine that provides:
- Secure code parsing and validation
- Dynamic namespace injection
- Safe execution with timeout
- Result serialization

#### BaseSession  
Abstract session management for:
- Provider-specific authentication
- Credential handling
- Configuration management

#### Security Sandbox
AST-based security layer featuring:
- Import validation
- Function call filtering  
- Execution time limits
- Memory protection

## 📦 Installation

### From TestPyPI
```bash
pip install -i https://test.pypi.org/simple/ syntropaibox
```

### With Extra Index (Recommended)
```bash
pip install -i https://test.pypi.org/simple/ syntropaibox --extra-index-url https://pypi.org/simple
```

### Development Installation
```bash
git clone https://github.com/paihari/syntropaibox
cd syntropaibox
pip install -e .
```

## 🔧 Usage Examples

### Basic Provider Implementation

```python
from syntropaibox.mcp.base import BaseQuerier, BaseSession, DEFAULT_ALLOWED_MODULES
import argparse

class MyCloudSession(BaseSession):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @classmethod
    def configure_parser(cls, parser: argparse.ArgumentParser):
        parser.add_argument('--api-key', required=True)
    
    @classmethod  
    def from_args(cls, args: argparse.Namespace) -> "MyCloudSession":
        return cls(api_key=args.api_key)

class MyCloudQuerier(BaseQuerier):
    def __init__(self):
        session = MyCloudSession.from_args(args)
        
        namespace = {
            "mycloud": my_cloud_sdk,
            "session": session,
        }
        
        allowed_prefixes = ("mycloud",)
        custom_modules = DEFAULT_ALLOWED_MODULES.union({"mycloud"})
        
        super().__init__(allowed_prefixes, custom_modules, namespace)
```

### Secure Code Execution

```python
from syntropaibox.mcp.base import BaseQuerier

querier = MyCloudQuerier()

# Safe execution of user code
code_snippet = """
import mycloud
client = mycloud.Client(session.api_key)
result = client.list_resources()
"""

result = querier.execute_query(code_snippet)
print(result)  # JSON serialized response
```

### Custom Security Rules

```python
from syntropaibox.mcp.sandbox import CodeExecutor

class CustomExecutor(CodeExecutor):
    def visit_Call(self, node):
        # Add custom function restrictions
        if isinstance(node.func, ast.Name) and node.func.id == "dangerous_function":
            raise ValueError("Function not allowed")
        return super().visit_Call(node)
```

## 🛡️ Security Features

### AST Validation Pipeline
1. **Syntax Parsing**: Code is parsed into Abstract Syntax Tree
2. **Import Analysis**: All imports are validated against whitelist
3. **Function Validation**: Dangerous functions are blocked
4. **Execution**: Code runs in controlled namespace with timeout

### Whitelisted Modules
Default allowed modules include:
```python
DEFAULT_ALLOWED_MODULES = {
    "operator", "json", "datetime", "pytz", "dateutil", 
    "re", "time", "sys", "base64", "pydantic", "pandas"
}
```

### Safe Builtins
Only safe built-in functions are available:
```python
DEFAULT_BUILTINS_WHITELIST = [
    "dict", "list", "tuple", "set", "str", "int", "float", "bool",
    "len", "max", "min", "sorted", "filter", "map", "sum", "any", "all",
    "__import__", "hasattr", "getattr", "isinstance", "print"
]
```

## 🌟 Ecosystem Integration

### Supported MCP Servers
- **[AWS MCP Server](https://github.com/paihari/documentation-syntropai/tree/main/mcp-server-for-aws)**: Amazon Web Services integration
- **[Azure MCP Server](https://github.com/paihari/documentation-syntropai/tree/main/mcp-server-azure)**: Microsoft Azure integration
- **[OCI MCP Server](https://github.com/paihari/documentation-syntropai/tree/main/mcp-server-oci)**: Oracle Cloud Infrastructure integration
- **[Finviz MCP Server](https://github.com/paihari/documentation-syntropai/tree/main/mcp_finviz)**: Financial data integration

### Extension Pattern
```python
# Easy to extend for new providers
class NewCloudQuerier(BaseQuerier):
    def __init__(self):
        # Provider-specific setup
        namespace = {"newsdk": new_cloud_sdk}
        allowed_prefixes = ("newsdk",)
        super().__init__(allowed_prefixes, custom_modules, namespace)
```

## 📋 Requirements

- **Python**: >= 3.10
- **Core Dependencies**:
  - `hatch >= 1.14.1`
  - `httpx >= 0.28.1` 
  - `pandas >= 2.3.1`
  - `pydantic >= 2.11.7`

## 🏆 Technical Advantages

### Compared to Traditional Approaches
- ✅ **Dynamic Service Support**: No hardcoded service catalogs
- ✅ **Security by Design**: AST validation prevents code injection
- ✅ **Provider Agnostic**: Same patterns work across all clouds
- ✅ **Future Proof**: New services work automatically
- ✅ **Production Ready**: Timeout, logging, error handling

### Architecture Benefits
- **Clean Abstractions**: Clear separation of concerns
- **Extensible Design**: Plugin-based architecture
- **Type Safety**: Full Pydantic integration
- **Memory Efficient**: Controlled execution environment

## 📚 Documentation

- **[Complete Ecosystem Documentation](https://github.com/paihari/documentation-syntropai)**
- **[Architecture Diagrams](https://github.com/paihari/documentation-syntropai/blob/main/ARCHITECTURE.md)**
- **API Reference**: Coming soon

## 🤝 Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md).

### Development Setup
```bash
git clone https://github.com/paihari/syntropaibox
cd syntropaibox
pip install -e ".[dev]"
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support & Contact

- **Main Documentation**: [SyntropAI MCP Ecosystem](https://github.com/paihari/documentation-syntropai)
- **Author**: Hari Bantwal
- **Email**: hpai.bantwal@gmail.com
- **Package**: [TestPyPI](https://test.pypi.org/project/syntropaibox/)

## 🔗 Related Links

- **[SyntropAI Ecosystem](https://github.com/paihari/documentation-syntropai)**: Complete project overview
- **[Architecture Documentation](https://github.com/paihari/documentation-syntropai/blob/main/ARCHITECTURE.md)**: Detailed system design
- **Individual MCP Servers**: AWS, Azure, OCI, Finviz implementations

---

*SyntropAIBox represents the cutting edge of secure, extensible MCP server development, providing the foundation for next-generation cloud service abstractions.*