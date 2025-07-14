from textwrap import dedent, indent
import json
from typing import Any, Callable


def pprint(data: Any, parse_func: Callable = None, layer: int = 1):
    """打印数据"""
    if parse_func and callable(parse_func):
        data = parse_func(data)
    if not isinstance(data, str):
        data = json.dumps(data, indent=4, ensure_ascii=False)

    print(indent(text=dedent(data), prefix=" " * 4 * layer))


def pprint2(data: Any, parse_func: Callable = None):
    pprint(data, parse_func, layer=2)


def pprint3(data: Any, parse_func: Callable = None):
    pprint(data, parse_func, layer=3)


if __name__ == "__main__":
    pprint(
        """
            a
        b
        c
    """
    )
