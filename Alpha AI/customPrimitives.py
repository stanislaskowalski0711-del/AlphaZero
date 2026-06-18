from dreamcoder.program import Primitive
from dreamcoder.grammar import Grammar
from dreamcoder.type import *


def primitives(object_id=None):
    """
    返回原语列表，供DREAMCODER的wake-G算法使用。
    
    Args:
        object_id: 可选的固定对象ID。如果提供，将使用 if_click(object_id, program) 格式。
                   程序格式将固定为: if_click(object_id, inner_program)
                   如果为 None，则使用通用 if_click 格式。
    
    类型签名示例：
    - 常量: tint, tbool, tlist(t0)
    - 一元函数: arrow(tint, tint)
    - 二元函数: arrow(tint, tint, tint)
    - 多态函数: arrow(t0, t0), arrow(tlist(t0), tlist(t0))
    
    实现函数示例：
    - 常量值直接使用值本身
    - 函数使用curried形式: lambda x: lambda y: x + y
    """
    # 定义具体类型：网格是 list(list(int))
    grid_type = tlist(tlist(tint))
    
    base_primitives = [
        # 无效果原语：返回输入本身
        Primitive("no_effect", arrow(grid_type, grid_type), 
                  lambda grid: grid),
        
        # 颜色转换原语
        Primitive("color_block", arrow(tint, tint, grid_type, grid_type), 
                  lambda from_color: lambda to_color: lambda grid: [
                      [to_color if cell == from_color else cell for cell in row] 
                      for row in grid
                  ]),
    ]
    
    # 必须指定 object_id
    if object_id is not None:
        # if_click_objectID : (grid->grid) -> grid->grid
        # 格式: if_click_objectID(inner_program)
        fixed_if_click = Primitive(
            f"if_click_{object_id}", 
            arrow(arrow(grid_type, grid_type), arrow(grid_type, grid_type)),
            lambda func: lambda state: func(state)
        )
        base_primitives.append(fixed_if_click)
    else:
        raise ValueError("必须提供 object_id 参数！")
    
    # 数字常量 (0-14，共15种)
    number_constants = [
        Primitive("0", tint, 0),
        Primitive("1", tint, 1),
        Primitive("2", tint, 2),
        Primitive("3", tint, 3),
        Primitive("4", tint, 4),
        Primitive("5", tint, 5),
        Primitive("6", tint, 6),
        Primitive("7", tint, 7),
        Primitive("8", tint, 8),
        Primitive("9", tint, 9),
        Primitive("10", tint, 10),
        Primitive("11", tint, 11),
        Primitive("12", tint, 12),
        Primitive("13", tint, 13),
        Primitive("14", tint, 14),
    ]
    
    return base_primitives + number_constants


def grammar(object_id, continuationType=None):
    """
    创建一个可被wake-G使用的Grammar对象。
    
    Args:
        object_id: 必须提供的固定对象ID。程序格式将固定为:
                   if_click(object_id, inner_program)
                   这对于"已知点击对象ID，合成解释程序"非常有用。
        continuationType: 可选的延续类型，用于限制生成程序的返回类型
    
    Returns:
        Grammar对象，可直接传递给explorationCompression或ecIterator
    
    示例:
        # 已知点击了对象ID=1
        g = grammar(object_id=1)
        # 程序将自动格式化为: if_click_1(inner_program)
    """
    base_primitives = primitives(object_id)
    grid_type = tlist(tlist(tint))
    
    if continuationType is None:
        continuationType = arrow(grid_type, grid_type)
    
    return Grammar.uniform(base_primitives, continuationType=continuationType)


def wrap_with_if_click(program, object_id):
    """
    将程序包装成 if_click(object_id, program) 格式。
    
    这个函数确保所有合成的程序都符合格式要求。
    
    Args:
        program: 原始程序（内层程序，如 color_block(1, 2)）
        object_id: 对象ID（可以是任意整数）
    
    Returns:
        包装后的程序: if_click(object_id, program)
        
    示例:
        program = color_block(1, 2)
        wrapped = wrap_with_if_click(program, object_id=1)
        # 结果: if_click(1, color_block(1, 2))
    """
    from dreamcoder.program import Application
    
    # 找到固定的 if_click_{object_id} 原语
    prims = primitives(object_id=object_id)
    fixed_if_click = None
    
    for p in prims:
        if p.name == f'if_click_{object_id}':
            fixed_if_click = p
            break
    
    if fixed_if_click:
        # 构建: if_click_objectID(program)
        return Application(fixed_if_click, program)
    else:
        # 如果找不到固定原语，创建通用包装
        # 找到通用 if_click 和数字常量
        for p in prims:
            if p.name == 'if_click':
                fixed_if_click = p
                break
    
    if fixed_if_click:
        # 找到对应的数字常量
        id_const = None
        for p in prims:
            if p.name == str(object_id):
                id_const = p
                break
        
        if id_const:
            return Application(Application(fixed_if_click, id_const), program)
    
    raise ValueError(f"无法包装程序: 找不到 if_click_{object_id} 原语")


def makeTasks(examples, requestType=None):
    """
    辅助函数：从示例数据创建任务。
    
    Args:
        examples: 示例列表，格式为 [(input1, output1), (input2, output2), ...]
        requestType: 可选的请求类型
    
    Returns:
        Task对象列表
    """
    from dreamcoder.task import Task
    
    tasks = []
    for i, (inp, out) in enumerate(examples):
        task_name = f"custom_task_{i}"
        if requestType is None:
            try:
                requestType = guess_arrow_type(examples)
            except:
                raise ValueError("无法自动推断类型，请提供requestType参数")
        
        task = Task(name=task_name,
                    request=requestType,
                    examples=[(inp, out)],
                    features=None)
        tasks.append(task)
    return tasks