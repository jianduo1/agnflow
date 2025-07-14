from typing import (
    Any,
    Literal,
    Union,
    Optional,
    get_args,
    get_origin,
    get_type_hints,
    is_typeddict,
)
from typing_extensions import NotRequired, Required
from types import UnionType, NoneType

# log = print
log = lambda *arg: ...


def check_type(obj, type_) -> bool:
    """检查obj是否符合复杂类型

    支持类型：
    - None Any Union Literal
    - NotRequired Required Optional TypedDict
    - list tuple dict set 泛型 复合类型
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
        for arg in args:
            if check_type(obj, arg):
                return True
        log(f"Union类型校验失败: {obj} 不是 {type_}")
        return False

    # 处理 Literal 类型
    if O is Literal:
        # Literal 类型检查值是否相等
        args = get_args(type_)
        if obj in args:
            return True
        log(f"Literal类型校验失败: {obj} 不是 {type_}")
        return False

    # 处理 NotRequired 类型
    if O is NotRequired:
        # NotRequired 类型表示可选字段，如果对象不存在该字段则返回 True
        # 如果存在该字段，则检查其值是否符合 NotRequired 包装的类型
        args = get_args(type_)
        if len(args) == 1:
            # 对于 NotRequired[T]，如果 obj 是 None 或者不存在，返回 True
            # 如果 obj 存在，则检查是否符合 T 类型
            if obj is None:
                return True
            return check_type(obj, args[0])
        return True

    # 处理 Required 类型
    if O is Required:
        # Required 类型表示必需字段，不能为 None
        # 如果 obj 是 None，返回 False
        # 如果 obj 存在，则检查是否符合 Required 包装的类型
        args = get_args(type_)
        if len(args) == 1:
            if obj is None:
                log(f"Required类型校验失败: {obj} 不能为 None")
                return False
            return check_type(obj, args[0])
        log(f"Required类型校验失败: {obj} 不能为 None")
        return False

    # 处理 Optional 类型
    if O is Optional:
        # Optional 类型表示可选字段，可以为 None 或指定类型
        args = get_args(type_)
        if len(args) == 1:
            # 对于 Optional[T]，如果 obj 是 None，返回 True
            # 如果 obj 存在，则检查是否符合 T 类型
            if obj is None:
                return True
            return check_type(obj, args[0])
        return True

    # TypedDict 递归校验
    if not O and is_typeddict(type_):
        try:
            annotations = get_type_hints(type_)
            required_keys = [k for k in annotations if annotations[k] is Required]
            optional_keys = [k for k in annotations if annotations[k] is NotRequired]
            total = getattr(type_, "__total__", True)
            # 检查必需字段
            for field in required_keys:
                if field not in obj:
                    log(f"TypedDict必填字段缺失: {field}")
                    return False
                if not check_type(obj[field], annotations[field]):
                    log(f"TypedDict必填字段校验失败: {field}")
                    return False
            # 检查可选字段
            for field in optional_keys:
                if field in obj and not check_type(obj[field], annotations[field]):
                    log(f"TypedDict可选字段校验失败: {field}")
                    return False
            # 检查多余字段
            if total:
                for k in obj:
                    if k not in annotations:
                        log(f"TypedDict多余字段: {k}")
                        return False
            return True
        except Exception as e:
            log(f"TypedDict校验异常: {e}")
            return True

    # 检查是否为非泛型
    if not O:
        return isinstance(obj, type_)

    # 检查是否为泛型
    if not isinstance(obj, O):
        log(f"泛型类型不匹配: {obj} 不是 {O}")
        return False
    elif isinstance(obj, dict):
        K, V = get_args(type_)
        if not all(check_type(k, K) and check_type(v, V) for k, v in obj.items()):
            log(f"泛型dict[K,V]校验失败: {obj}")
            return False
    elif isinstance(obj, tuple):
        if not all(check_type(i, T) for i, T in zip(obj, get_args(type_))):
            log(f"泛型tuple[T]校验失败: {obj}")
            return False
    elif isinstance(obj, list):
        T = get_args(type_)[0]
        if not all(check_type(i, T) for i in obj):
            log(f"泛型list[T]校验失败: {obj}")
            return False
    elif isinstance(obj, set):
        T = get_args(type_)[0]
        if not all(check_type(i, T) for i in obj):
            log(f"泛型set[T]校验失败: {obj}")
            return False
    return True


if __name__ == "__main__":
    from typing import TypedDict

    # print(check_type([("a", {"b": tuple()})], list[tuple[str, dict[str, tuple]]]))
    # print(check_type(None, type(None)))

    # print(check_type(None, NotRequired[int])) # type: ignore
    # print(check_type(None, Required[int])) # type: ignore
    # print(check_type(None, Optional[int]))
    class C(TypedDict):
        n: int
    class B(TypedDict):
        n: int
        t: NotRequired[list[C]]

    class A(TypedDict, total=False):
        n: int
        b: NotRequired[list[B]]

    # print(check_type({"a": 1}, A))
    # print(check_type({"a":1,"b":[]}, A))
    # print(check_type({"a": 1, "b": [{"n": 2}]}, A))
    
    from agnflow.agent.cot import Plan
    data = [
        {"description": "定义智能体CoT", "status": "Pending"},
        {"description": "查找CoT相关资料", "status": "Pending"},
        {"description": "分析CoT的核心特征", "status": "Pending"},
        {"description": "结论", "status": "Pending"},
    ]
    print(check_type(data, NotRequired[list[Plan]])) # type: ignore
