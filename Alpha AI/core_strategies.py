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


def gpt_hypothesis_generator(initial_screen, game_state):
    """
    调用GPT大模型生成通关目标假设
    
    Args:
        initial_screen: 初始游戏画面矩阵
        game_state: 当前游戏状态信息
    
    Returns:
        list: 多个候选通关目标假设
    """
    hypotheses = [
        "所有方块变为同一颜色",
        "特定图案匹配",
        "所有方块变为目标颜色",
        "触发特定事件序列"
    ]
    return hypotheses


def gpt_strategy_generator(environment_state, memory):
    """
    调用GPT大模型生成探索策略
    
    Args:
        environment_state: 当前环境状态
        memory: 长期记忆对象
    
    Returns:
        list: 多个候选探索策略
    """
    strategies = [
        "优先点击不同颜色的方块",
        "按区域顺序探索",
        "尝试点击边缘方块",
        "尝试点击中心方块"
    ]
    return strategies


def gpt_world_model_generator(interaction_history, objects):
    """
    调用GPT大模型构建世界模型（多object相互影响规律）
    
    Args:
        interaction_history: 交互历史记录列表
        objects: 所有对象信息
    
    Returns:
        dict: 世界模型（包含object相互影响规律）
    """
    world_model = {
        'object_relations': [],
        'effect_patterns': [],
        'causal_rules': []
    }
    
    for interaction in interaction_history:
        obj_id = interaction.get('object_id')
        effect = interaction.get('effect')
        if effect and effect != 'no_effect':
            world_model['effect_patterns'].append({
                'object_id': obj_id,
                'effect': effect
            })
    
    return world_model


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
