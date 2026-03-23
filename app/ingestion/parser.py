import ast


def extract_python_symbols(content: str):
    symbols = []

    try:
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                symbols.append({
                    "name": node.name,
                    "type": "function",
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno)
                })
            elif isinstance(node, ast.AsyncFunctionDef):
                symbols.append({
                    "name": node.name,
                    "type": "async_function",
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno)
                })
            elif isinstance(node, ast.ClassDef):
                symbols.append({
                    "name": node.name,
                    "type": "class",
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno)
                })

    except Exception:
        pass

    return symbols
