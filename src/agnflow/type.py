from typing import Any,  Literal, get_args, get_origin, Union
from types import UnionType, NoneType

def check_generic_type(obj, type_) -> bool:
    """检查obj是否符合复杂类型

    支持类型：None、Any、Union、Literal、list、tuple、dict、set、泛型、复合类型

    示例：
    print(check_deep_type([("a",{"b":tuple()})],
                            list[tuple[str, dict[str, tuple]]]))
    print(check_deep_type(None,type(None)))
    """
    # 处理 None 类型
    if type_ is NoneType or type_ is None:
        return obj is None

    # 处理 Any 类型
    if type_ is Any:
        return True

    O = get_origin(type_)

    # 处理联合类型 (Union, |)
    if O in (Union, UnionType):
        # 对于 Union 类型，只要匹配其中一个类型即可
        args = get_args(type_)
        return any(check_generic_type(obj, arg) for arg in args)

    # 处理 Literal 类型
    if O is Literal:
        # Literal 类型检查值是否相等
        args = get_args(type_)
        return obj in args

    # 检查是否为非泛型
    if not O:
        return isinstance(obj, type_)

    # 检查是否为泛型
    if not isinstance(obj, O):
        return False
    elif isinstance(obj, dict):
        K, V = get_args(type_)
        if not all(check_generic_type(k, K) and check_generic_type(v, V) for k, v in obj.items()):
            return False
    elif isinstance(obj, tuple):
        if not all(check_generic_type(i, T) for i, T in zip(obj, get_args(type_))):
            return False
    elif isinstance(obj, list):
        T = get_args(type_)[0]
        if not all(check_generic_type(i, T) for i in obj):
            return False
    elif isinstance(obj, set):
        T = get_args(type_)[0]
        if not all(check_generic_type(i, T) for i in obj):
            return False
    return True
