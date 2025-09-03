import ast
from typing import List

DEFAULT_BUILTINS_WHITELIST = [
    # Core types
    "dict", "list", "tuple", "set", "str", "int", "float", "bool",
    
    # Common functions
    "len", "max", "min", "sorted", "filter", "map", "sum", "any", "all",
    "__import__", "hasattr", "getattr", "isinstance", "print",

    # Exceptions
    "BaseException", "Exception", "ImportError", "ValueError", "KeyError", "TypeError",
    "IndexError", "AttributeError", "RuntimeError"
]


def exec_with_timeout(compiled_code, local_ns, seconds: int = 2):
    import signal
    def handler(signum, frame):
        raise TimeoutError("Code execution took too long")

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)
    try:
        exec(compiled_code, local_ns)
    finally:
        signal.alarm(0)


def create_safe_builtins(whitelist: List[str] = None) -> dict:
    """
    Creates a dictionary of safe built-in functions by whitelisting selected names.
    Handles __builtins__ being either a dict or module.

    Args:
        whitelist (List[str]): A list of built-in names to allow. If None, uses default whitelist.

    Returns:
        dict: A dictionary of whitelisted built-ins
    """
    whitelist = whitelist or DEFAULT_BUILTINS_WHITELIST
    src = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__

    safe_builtins = {}
    for name in whitelist:
        if name in src:
            safe_builtins[name] = src[name]
    return safe_builtins

class CodeExecutor(ast.NodeTransformer):
    def __init__(self):
        self.has_result = False
        self.imported_modules = set()

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'result':
                self.has_result = True
        return node

    def visit_Import(self, node):
        for alias in node.names:
            self.imported_modules.add(alias.name)
        return node

    def visit_ImportFrom(self, node):
        self.imported_modules.add(node.module)
        return node

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile"}:
            raise ValueError(f"Usage of '{node.func.id}' is not allowed.")
        return self.generic_visit(node)