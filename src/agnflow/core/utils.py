import inspect


def get_code_line() -> list[str]:
    """基于调用栈获取代码行

    ```python
    1 + 1; l = get_code_line()
    print(l)
    out:
    ['1 + 1']
    ```
    """
    stack = inspect.stack()[1:]
    try:

        def handle(line):
            if ";" in line and "get_code_line" in line:
                line = ";".join([i for i in line.split(";") if "get_code_line" not in i])
            return line

        return [handle(frame.code_context[0].strip()) for frame in stack if frame.code_context]
    finally:
        del stack
