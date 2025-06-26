import inspect,re
class A:
    def __init__(self) -> None:
        self._get_name()
        
    def _get_name(self):
        """设置实例名称"""
        stack = inspect.stack()
        try:
            # stack[0]: _collect_names
            # stack[1]: _Conn.__init__
            # stack[2]: ...
            # stack[3]: 用户代码中调用构造函数的帧。
            if len(stack) > 1:
                caller_frame = stack[-1]
                if caller_frame.code_context:
                    line = caller_frame.code_context[0].strip()
                    match = re.match(r"^\s*(\w+)\s*=\s*" + self.__class__.__name__ + r"\(", line)
                    if match:
                        self.name = match.group(1)

        except Exception:
            self.name = self.__class__.__name__
        finally:
            # 避免引用循环
            # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
            del stack


# A()[(2, 3, 4)]

# A()[1:2, 1:3, 1:4]
# A()[1:(2, 3, 4)]

# A()[:(2, 3, 4):]
# A()[(2, 3, 4):(2, 3, 4)]


a = A()
print(a.name)