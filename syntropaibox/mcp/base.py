import ast
import json
import logging
from typing import Any
# from syntropAIkit.mcp.sandbox import CodeExecutor, create_safe_builtins
from .sandbox import create_safe_builtins, CodeExecutor

logger = logging.getLogger("BaseQuerier")


class BaseQuerier:
    def __init__(self, allowed_prefixes: set[str], allowed_modules: set[str], namespace: dict[str, Any]):
        self.allowed_modules = allowed_modules
        self.allowed_prefixes = allowed_prefixes
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
