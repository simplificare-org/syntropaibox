import ast
import json
import logging
from typing import Any
# from syntropAIkit.mcp.sandbox import CodeExecutor, create_safe_builtins
from .sandbox import create_safe_builtins, CodeExecutor
from abc import ABC, abstractmethod
import argparse

from operator import itemgetter

logger = logging.getLogger("BaseQuerier")


DEFAULT_ALLOWED_MODULES = {
    "operator", "json", "datetime", "pytz",
    "dateutil", "re", "time", "sys", "base64", "pydantic", "pandas"
}

class BaseSession(ABC):
    @classmethod
    @abstractmethod
    def from_args(cls, args: argparse.Namespace) -> "BaseSession":
        """Instantiate session using parsed CLI/environment arguments"""
        pass

    @classmethod
    @abstractmethod
    def configure_parser(cls, parser: argparse.ArgumentParser):
        """Inject provider-specific CLI options"""
        pass



class BaseQuerier:
    def __init__(self, allowed_prefixes: set[str], allowed_modules: set[str], namespace: dict[str, Any]):
        self.allowed_modules = allowed_modules or DEFAULT_ALLOWED_MODULES
        self.allowed_prefixes = allowed_prefixes

        # Inject common namespace defaults
        namespace["itemgetter"] = itemgetter
        namespace["result"] = None
        self.namespace = namespace

    def execute_query(self, code_snippet: str) -> str:
        logger.info(f"Executing query snippet:\n{code_snippet}")
        try:
            tree = ast.parse(code_snippet)
            executor = CodeExecutor()
            executor.visit(tree)

            unauthorized = {
                mod for mod in executor.imported_modules
                if mod not in self.allowed_modules
                if not mod.startswith(self.allowed_prefixes) and mod not in self.allowed_modules
            }
            if unauthorized:
                return json.dumps({"error": f"Unauthorized imports: {unauthorized}"})

            self.namespace["__builtins__"] = create_safe_builtins()
            compiled = compile(tree, "<string>", "exec")
            exec(compiled, self.namespace)

            result = self.namespace.get("result")
            if not executor.has_result:
                return json.dumps({"error": "Missing 'result' variable in code."})

            if result is not None:
                if hasattr(result, 'dict'):
                    result = result.dict()
                elif hasattr(result, 'to_dict'):
                    result = result.to_dict()
                return json.dumps(result, default=str)

            return json.dumps({"error": "Result is None"})

        except SyntaxError as e:
            return json.dumps({"error": f"Syntax error: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def build_code_snippet_schema(self, sdk_description: str) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code_snippet": {
                    "type": "string",
                    "description": (
                        f"Python code using {sdk_description}. "
                        "The code must assign the result to a variable named 'result'."
                    )
                }
            },
            "required": ["code_snippet"]
    }

    def run_code_tool(self, arguments: dict[str, Any]) -> str:
        if not arguments or "code_snippet" not in arguments:
            raise ValueError("Missing code_snippet argument")

        return self.execute_query(arguments["code_snippet"])
    
