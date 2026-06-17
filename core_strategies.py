"""
Alpha AI 核心逻辑入口
其他开发者可以通过修改这个文件来自定义：
- 探索策略
- 点击决策
- 记忆管理
- 学习逻辑

无需修改 curiosity_exploration.py 或其他核心文件
"""

# ==================== 核心接口（已被主程序使用） ====================

def select_grid_coordinate(object_grid_coordinates):
    """
    选择要点击的网格坐标
    
    Args:
        object_grid_coordinates: object包含的所有网格坐标列表
        
    Returns:
        (x, y): 选中的网格坐标
    """
    import random
    
    # 默认策略：随机选择一个网格坐标
    return random.choice(object_grid_coordinates)


def classify_effect(program_str):
    """
    分类点击效果
    
    Args:
        program_str: 程序字符串
        
    Returns:
        str: 效果类型 ('no_effect', 'has_effect')
    """
    # 默认策略：判断是否为恒等函数
    if "(lambda $0)" in program_str and "color_block" not in program_str:
        return 'no_effect'
    elif "(lambda $0)" not in program_str:
        return 'has_effect'
    else:
        return 'has_effect'


# ==================== 高级扩展接口（未来改进趋向） ====================
# 以下接口对应 README 中提到的未来改进方向
# 开发者可以实现这些接口来扩展系统能力

def sleep_recognition(interaction_history):
    """
    Sleep Recognition - 根据交互历史训练神经网络识别规律

    Args:
        interaction_history: 多次交互的历史记录列表

    Returns:
        dict: 识别到的规律特征
    """
    patterns = {}
    for interaction in interaction_history:
        obj_id = interaction.get('object_id')
        effect = interaction.get('effect')
        if obj_id not in patterns:
            patterns[obj_id] = []
        patterns[obj_id].append(effect)
    return patterns


def sleep_program_synthesis(recognized_patterns, few_shot_feedback):
    """
    Sleep G - 根据少数交互反馈形成真正的规律程序

    Args:
        recognized_patterns: 从 sleep_recognition 识别到的规律特征
        few_shot_feedback: 少数几次交互的反馈

    Returns:
        str: 合成出的规律程序
    """
    return "(lambda $0)"


def curiosity_mechanism(objects, memory):
    """
    好奇心机制 - 基于内在动机进行自主探索
    示例实现：优先探索未探索过或探索次数最少的对象

    Args:
        objects: 所有可探索的objects列表
        memory: 长期记忆对象

    Returns:
        object_id: 最值得探索的object ID
    """
    import random
    
    unexplored = [obj for obj in objects if obj.get('id') not in memory]
    if unexplored:
        return random.choice(unexplored)['id']
    
    min_explored = min(objects, key=lambda x: memory.get(x.get('id'), {}).get('explore_count', 0))
    return min_explored['id']


def belief_decay_pruning(object_id, memory):
    """
    改造剪枝策略
    示例实现：根据历史交互结果动态评估对象价值

    Args:
        object_id: object的ID
        memory: 长期记忆对象

    Returns:
        float: 信念度值 (0.0 - 1.0)
    """
    obj_memory = memory.get(object_id, {})
    explore_count = obj_memory.get('explore_count', 0)
    effect_count = obj_memory.get('effect_count', 0)
    
    if explore_count == 0:
        return 0.5
    
    base_belief = effect_count / max(explore_count, 1)
    
    decay_factor = 0.95 ** explore_count
    
    return min(1.0, max(0.0, base_belief * decay_factor))


def interaction_history_recorder(action, result, timestamp):
    """
    记录交互历史过程

    Args:
        action: 点击探索动作 (dict)
        result: 动作结果 (dict)
        timestamp: 时间戳

    Returns:
        dict: 更新后的交互历史记录
    """
    return {
        'action': action,
        'result': result,
        'timestamp': timestamp,
        'processed': False
    }


def similarity_recognition(program_a, program_b):
    """
    识别相似性和共同性 - 用于类比扩展

    Args:
        program_a: 程序A字符串
        program_b: 程序B字符串

    Returns:
        float: 相似度分数 (0.0 - 1.0)
    """
    common_tokens = set(program_a.split()) & set(program_b.split())
    all_tokens = set(program_a.split()) | set(program_b.split())
    
    if not all_tokens:
        return 0.0
    
    return len(common_tokens) / len(all_tokens)


def intuition_network(exploration_history, pruning_history, new_environment):
    """
    直觉神经网络 - 模仿人类直觉进行探索
    示例实现：基于历史经验推荐高价值探索目标

    Args:
        exploration_history: 历史探索过程列表
        pruning_history: 历史剪枝过程列表
        new_environment: 新环境状态字典

    Returns:
        object_id: 推荐的下一个探索目标
    """
    import random
    
    objects = new_environment.get('objects', [])
    
    if not objects:
        return None
    
    high_value_objects = []
    for obj in objects:
        obj_id = obj.get('id')
        has_effect = any(
            hist.get('object_id') == obj_id and hist.get('has_effect')
            for hist in exploration_history
        )
        if has_effect:
            high_value_objects.append(obj_id)
    
    if high_value_objects:
        return random.choice(high_value_objects)
    
    return random.choice(objects)['id']


# ==================== 策略注册 ====================
# 在这里注册你想要使用的策略
# 修改后重启程序即可生效

ACTIVE_STRATEGIES = {
    'grid_selection': select_grid_coordinate,
    'effect_classification': classify_effect,
}
