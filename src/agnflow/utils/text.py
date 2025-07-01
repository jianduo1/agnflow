from textwrap import dedent, indent


class Text:
    """
    一个用于处理文本的类，支持indent和dedent操作
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __lshift__(self, other) -> str:
        """重载 << 相当于 dedent(self)"""
        return dedent(text=other)

    def __rshift__(self, other) -> str:
        """重载 >> 相当于 indent(self)"""
        return indent(text=other, **self.kwargs)


if __name__ == "__main__":
    text = (
        Text(prefix="    ")
        >> """
    Hello, World!
    """
    )
    print(text)
