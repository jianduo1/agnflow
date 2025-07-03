import inspect


def get_lines(back: int = 0) -> list[str]:
    stack = inspect.stack()[1:]

    try:
        if back == 0:
            for frame in stack:
                code = frame.code_context[0].strip()
                if code and ";" in code and "get_lines" in code:
                    return ";".join([i for i in code.split(";") if "get_lines" not in i])
        return [frame.code_context[0].strip() for frame in stack if frame.code_context][back if back < len(stack) else len(stack)-1]
    finally:
        del stack


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


if __name__ == "__main__":
    ...

    def a():
        b()

    def b():
        (1234)
        l = get_lines(22)
        print(l)

    a()
