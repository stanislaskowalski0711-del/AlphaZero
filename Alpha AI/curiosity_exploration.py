"""
ARC-AGI-3 好奇心探索模块
使用 config.py 配置参数
使用 core_strategies.py 自定义核心逻辑
"""
import arc_agi
import os
import numpy as np
import random
import time
import cv2
from datetime import datetime

# 导入配置文件
from config import *

# 导入核心策略（可自定义）
from core_strategies import ACTIVE_STRATEGIES

# 设置API Key
os.environ["ARC_API_KEY"] = ARC_API_KEY

# 初始化ARCAGI3环境
arc = arc_agi.Arcade()
env = arc.make(GAME_NAME)
obs = env.reset()

# 导入对象类别定义
from categories import category_1, category_2, category_3, category_4

# 导入坐标计算方法
from grid_coordinates import (
    get_grid_coordinate,
    GRID_TOP_LEFT_X,
    GRID_TOP_LEFT_Y,
    GRID_ORIGIN,
    X_AXIS_DIRECTION,
    Y_AXIS_DIRECTION
)

# 导入画面和矩阵保存模块
from frame_saver import (
    save_frame_with_grid,
    save_object_matrix,
    extract_object_matrix,
    convert_frame_to_matrix,
    COLOR_MAP
)

# 导入DreamCoder的wake-G算法
import sys
dreamcoder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ec-master', 'ec-master')
if dreamcoder_path not in sys.path:
    sys.path.append(dreamcoder_path)

# 从DreamCoder导入必要模块
from dreamcoder.dreamcoder import explorationCompression
from dreamcoder.grammar import Grammar
from dreamcoder.task import Task
from dreamcoder.type import *
from dreamcoder.frontier import Frontier

# 导入自定义原语库
from customPrimitives import grammar, primitives, wrap_with_if_click

# 导入程序记忆库
from long_term_memory import memory

# 帧保存和视频录制
frame_count = 0
frame_output_dir = None
video_writer = None
video_path = None


def init_video_recorder():
    """初始化帧保存和视频录制"""
    global frame_count, frame_output_dir, video_writer, video_path
    
    if not ENABLE_VIDEO_RECORDING:
        print("视频录制已禁用")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    frame_output_dir = f"frames_{timestamp}"
    os.makedirs(frame_output_dir, exist_ok=True)
    frame_count = 0
    
    # 初始化视频写入器
    video_path = f"curiosity_exploration_{timestamp}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = VIDEO_FPS
    frame_size = (64 * SCALE_FACTOR, 64 * SCALE_FACTOR)
    video_writer = cv2.VideoWriter(video_path, fourcc, fps, frame_size)
    
    print(f"帧保存目录: {frame_output_dir}")
    print(f"视频输出路径: {video_path}")
    print(f"视频帧率: {fps} fps")
    print(f"视频分辨率: {frame_size[0]}x{frame_size[1]}")


def add_video_frame(frame_data, click_pos=None, category_index=None, object_id=None, frame_type=None, phase=None, attempt_num=None):
    """保存一帧为PNG图片并写入视频
    """
    global frame_count, frame_output_dir, video_writer
    
    if frame_output_dir is None:
        return
    
    # 处理frame数据类型 - 处理各种可能的嵌套结构
    if isinstance(frame_data, list):
        if len(frame_data) == 1:
            frame_data = frame_data[0]
        if isinstance(frame_data, list):
            try:
                frame_data = np.array(frame_data)
            except Exception as e:
                print(f"警告: 无法将list转换为numpy数组: {e}")
                return
    
    if not isinstance(frame_data, np.ndarray):
        return
    
    if frame_data.size == 0:
        return
    
    shape = frame_data.shape
    
    # 处理可能的额外维度
    processed_frame = frame_data
    if len(shape) == 4 and shape[0] == 1:
        processed_frame = frame_data.squeeze(0)
        shape = processed_frame.shape
    elif len(shape) == 3 and shape[0] == 1:
        processed_frame = frame_data.squeeze(0)
        shape = processed_frame.shape
    elif len(shape) == 3 and shape[0] > 1:
        processed_frame = frame_data[0]
        shape = processed_frame.shape
    
    # 检查是否为颜色索引矩阵 (64x64，值范围0-15)
    is_color_index = len(shape) == 2 and processed_frame.max() <= 15 and processed_frame.min() >= 0
    
    # 处理颜色索引矩阵 (64x64，值范围0-15)
    if is_color_index:
        height, width = shape
        frame_rgb = np.zeros((height, width, 3), dtype=np.uint8)
        
        for i in range(height):
            for j in range(width):
                color_idx = int(processed_frame[i, j])
                if color_idx in COLOR_MAP:
                    frame_rgb[i, j] = COLOR_MAP[color_idx]
                else:
                    frame_rgb[i, j] = (128, 128, 128)
        
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    elif len(shape) == 2:
        frame_bgr = cv2.cvtColor(processed_frame.astype(np.uint8), cv2.COLOR_GRAY2BGR)
    elif len(shape) == 3 and shape[2] == 4:
        frame_bgr = cv2.cvtColor(processed_frame, cv2.COLOR_RGBA2BGR)
    elif len(shape) == 3 and shape[2] == 3:
        frame_bgr = cv2.cvtColor(processed_frame, cv2.COLOR_RGB2BGR)
    else:
        return
    
    if frame_bgr is None:
        return
    
    # 放大 (64x64 -> 1024x1024)
    scale_factor = 16
    frame_bgr = cv2.resize(frame_bgr, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_NEAREST)
    
    # 添加网格线
    grid_size = scale_factor
    height, width = frame_bgr.shape[:2]
    grid_color = (180, 180, 180)
    for i in range(0, width + 1, grid_size):
        cv2.line(frame_bgr, (i, 0), (i, height), grid_color, 1)
    for i in range(0, height + 1, grid_size):
        cv2.line(frame_bgr, (0, i), (width, i), grid_color, 1)
    
    # 添加点击标记 (黄色方框)
    if click_pos:
        x, y = click_pos
        if hasattr(x, 'shape'):
            x_val = int(x.flat[0])
            y_val = int(y.flat[0])
        else:
            x_val = int(x)
            y_val = int(y)
        
        x_scaled = x_val * scale_factor
        y_scaled = y_val * scale_factor
        
        top_left = (x_scaled, y_scaled)
        bottom_right = (x_scaled + grid_size, y_scaled + grid_size)
        cv2.rectangle(frame_bgr, top_left, bottom_right, (0, 255, 255), 2)
    
    # 写入视频
    if video_writer is not None:
        video_writer.write(frame_bgr)
    
    # 生成文件名并保存PNG
    frame_count += 1
    
    if phase == 'explore':
        filename = os.path.join(frame_output_dir, f"cat{category_index}_obj{object_id}_{frame_type}.png")
    elif phase == 'win_attempt':
        filename = os.path.join(frame_output_dir, f"attempt{attempt_num}_cat{category_index}_obj{object_id}_{frame_type}.png")
    else:
        filename = os.path.join(frame_output_dir, f"frame_{frame_count:04d}.png")
    
    cv2.imwrite(filename, frame_bgr)


def convert_grid_to_rgb(grid):
    """将颜色索引网格转换为RGB图像"""
    # 处理list类型
    if isinstance(grid, list):
        grid = np.array(grid)
    
    height, width = grid.shape[:2]
    rgb = np.zeros((height, width, 3), dtype=np.uint8)
    
    for i in range(height):
        for j in range(width):
            val = grid[i, j]
            # 处理可能的数组值
            if hasattr(val, 'shape'):  # numpy数组
                color_idx = int(val.flat[0])
            else:
                color_idx = int(val)
            if color_idx in COLOR_MAP:
                rgb[i, j] = COLOR_MAP[color_idx]
            else:
                rgb[i, j] = (128, 128, 128)
    
    return rgb


def release_video_recorder():
    """释放帧保存和视频录制器"""
    global frame_count, frame_output_dir, video_writer, video_path
    
    # 释放视频写入器
    if video_writer is not None:
        video_writer.release()
        print(f"视频保存完成: {video_path}")
        video_writer = None
        video_path = None
    
    if frame_output_dir:
        print(f"帧保存完成: {frame_output_dir}, 共 {frame_count} 帧")
    
    frame_count = 0
    frame_output_dir = None


def run_program_synthesis(object_id, input_matrix, output_matrix):
    """
    使用DreamCoder进行程序合成

    Args:
        object_id: 点击的对象ID
        input_matrix: 点击前的矩阵
        output_matrix: 点击后的矩阵

    Returns:
        合成的程序
    """
    grid_type = tlist(tlist(tint))

    # 创建语法（使用固定的object_id）
    g = grammar(object_id=object_id)

    # 创建任务：输入->输出示例
    # 将numpy数组转换为Python列表
    input_list = input_matrix.tolist() if hasattr(input_matrix, 'tolist') else list(input_matrix)
    output_list = output_matrix.tolist() if hasattr(output_matrix, 'tolist') else list(output_matrix)

    task = Task(
        name=f"click_object_{object_id}",
        request=arrow(grid_type, grid_type),
        examples=[((input_list,), output_list)],
        features=None
    )

    print(f"\n{'='*60}")
    print(f"开始程序合成...")
    print(f"Object ID: {object_id}")
    print(f"输入矩阵形状: {input_matrix.shape}")
    print(f"输出矩阵形状: {output_matrix.shape}")
    print(f"{'='*60}")

    # 调用DreamCoder的wake-G算法
    result = explorationCompression(
        grammar=g,
        tasks=[task],
        iterations=1,
        enumerationTimeout=60,
        maximumFrontier=10,
        useRecognitionModel=False,
        solver='python',
        topK=1,
    )

    # 获取合成结果
    frontiers = result.allFrontiers

    for t, frontier in frontiers.items():
        if frontier.entries:
            # 过滤：只保留 logLikelihood=0 的程序
            frontier.filterByExactZeroLikelihood()

            if frontier.entries:
                # 按 MDL 排序取最优
                frontier = frontier.topKByMDL(1)
                entry = frontier.entries[0]

                print(f"\n找到解释程序:")
                print(f"  内层程序: {entry.program}")
                print(f"  logPrior (MDL): {entry.logPrior}")
                print(f"  logLikelihood: {entry.logLikelihood}")

                # 包装成 if_click_objectID 格式
                wrapped_program = wrap_with_if_click(entry.program, object_id)
                print(f"  完整程序: {wrapped_program}")

                # 验证程序
                fn = wrapped_program.evaluate([])
                actual_output = fn(input_list)
                is_correct = actual_output == output_list

                print(f"\n验证结果:")
                print(f"  期望输出: {output_list}")
                print(f"  实际输出: {actual_output}")
                print(f"  正确: {'YES' if is_correct else 'NO'}")

                # 将合成的程序存储到程序记忆
                if is_correct:
                    mdl_value = -entry.logPrior
                    program_str = str(wrapped_program)
                    memory.store_synthesized_program(object_id, program_str, input_list, output_list, mdl_value)
                    print(f"  程序已存储到程序记忆")

                return wrapped_program
            else:
                print("没有找到 logLikelihood=0 的程序")
        else:
            print("未找到解决方案")

    return None


def _explore_single_category(selected_category, all_categories):
    """探索单个category"""
    global env

    category_index = all_categories.index(selected_category) + 1  # 编号从1开始

    # 使用策略选择object（可自定义）
    # 注意：这里保持原有逻辑，因为策略选择在curiosity_exploration()中进行
    selected_object = random.choice(selected_category)
    object_id = selected_object["id"]
    object_index = selected_category.index(selected_object) + 1  # 编号从1开始

    # 获取object的所有组成网格坐标
    grid_coordinates = selected_object["grid_coordinates"]

    # 使用策略选择网格坐标（可自定义）
    grid_selection_strategy = ACTIVE_STRATEGIES['grid_selection']
    selected_coordinate = grid_selection_strategy(grid_coordinates)
    coordinate_index = grid_coordinates.index(selected_coordinate) + 1  # 编号从1开始

    # 使用坐标计算方法找到对应的网格
    x, y = selected_coordinate
    grid = get_grid_coordinate(x, y)

    # 显示选择信息
    print(f"\n{'='*60}")
    print(f"好奇心探索信息")
    print(f"{'='*60}")
    print(f"选择的 Category 编号: {category_index}")
    print(f"选择的 Object 编号: {object_index}")
    print(f"Object ID: {object_id}")
    print(f"Object 的网格坐标列表: {grid_coordinates}")
    print(f"选择的网格坐标索引: {coordinate_index}")
    print(f"选择的网格坐标 (x, y): ({x}, {y})")
    print(f"转换后的点击坐标 (grid): {grid}")
    print(f"{'='*60}")

    # 获取点击前的画面
    obs = env.reset()
    frame_before = obs.frame
    
    # 转换为矩阵
    frame_matrix = convert_frame_to_matrix(frame_before)
    object_matrix_before = extract_object_matrix(frame_matrix, grid_coordinates)
    
    # 保存点击前画面 - 探索阶段
    print(f"=== 保存点击前画面: cat{category_index}_obj{object_id}_before.png ===")
    try:
        add_video_frame(frame_before, click_pos=grid, category_index=category_index, 
                        object_id=object_id, frame_type='before', phase='explore')
        print(f"成功保存点击前画面")
    except Exception as e:
        print(f"保存点击前画面失败: {e}")
    time.sleep(EXPLORATION_DELAY)

    # 在游戏画面中点击该网格
    click_x, click_y = grid
    print(f"=== 执行点击: ({click_x}, {click_y}) ===")
    result = env.step(action=6, data={'x': click_x, 'y': click_y})
    
    # 获取点击后的画面并转换为矩阵
    print(f"=== 获取点击后画面 ===")
    frame_after = None
    try:
        frame_after = result.frame
        if frame_after is None:
            print(f"警告: 点击后画面为空，使用点击前画面")
            frame_after = frame_before
        print(f"成功获取点击后画面")
    except Exception as e:
        print(f"获取点击后画面失败: {e}")
        frame_after = frame_before
    
    result_matrix = convert_frame_to_matrix(frame_after)
    object_matrix_after = extract_object_matrix(result_matrix, grid_coordinates)
    
    # 保存点击后画面 - 探索阶段
    print(f"=== 保存点击后画面: cat{category_index}_obj{object_id}_after.png ===")
    try:
        add_video_frame(frame_after, click_pos=grid, category_index=category_index, 
                        object_id=object_id, frame_type='after', phase='explore')
        print(f"成功保存点击后画面")
    except Exception as e:
        print(f"保存点击后画面失败: {e}")
    time.sleep(EXPLORATION_DELAY)

    # 生成时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 保存点击前的画面和object矩阵
    save_frame_with_grid(frame_matrix, f"frame_{timestamp}.png")
    save_object_matrix(object_matrix_before, f"object_matrix_before_{timestamp}.txt",
                       object_id, grid_coordinates, click_x, click_y, "Before Click")

    # 保存点击后的画面和object矩阵
    save_frame_with_grid(result_matrix, f"result_{timestamp}.png", click_pos=(click_x, click_y))
    save_object_matrix(object_matrix_after, f"object_matrix_after_{timestamp}.txt",
                       object_id, grid_coordinates, click_x, click_y, "After Click")

    # 运行程序合成（带超时保护）
    print(f"=== 开始程序合成: cat{category_index}_obj{object_id} ===")
    synthesized_program = None
    try:
        synthesized_program = run_program_synthesis(object_id, object_matrix_before, object_matrix_after)
        print(f"程序合成完成")
    except Exception as e:
        print(f"程序合成失败: {e}")
        import traceback
        traceback.print_exc()

    # 如果程序合成成功，为同一category内的其他object也存储相同的程序记忆
    if synthesized_program:
        program_str = str(synthesized_program)
        input_list = object_matrix_before.tolist()
        output_list = object_matrix_after.tolist()

        # 获取内层程序（去掉if_click包装）
        # 例如: (if_click_17 (lambda (color_block 9 8 $0))) -> (lambda (color_block 9 8 $0))
        inner_program = program_str.split('(if_click_')[1].split(' ', 1)[1].rstrip(')')

        # 获取当前category的所有其他object
        other_objects = [obj for obj in selected_category if obj["id"] != object_id]
        if other_objects:
            print(f"\n为同一Category的其他object存储相同程序记忆...")
            for obj in other_objects:
                other_id = obj["id"]
                # 为每个object生成对应的程序字符串
                other_program_str = f"(if_click_{other_id} {inner_program})"
                memory.store_synthesized_program(other_id, other_program_str, input_list, output_list, 0.0)
                print(f"  Object ID {other_id}: {other_program_str}")

    return synthesized_program, selected_category


def curiosity_exploration():
    """基于好奇心探索对象并执行click操作 - 遍历所有category"""
    global env

    # 获取所有categories
    all_categories = [category_1, category_2, category_3, category_4]
    
    # 获取当前游戏画面
    env.reset()
    
    # 遍历所有category
    for i, selected_category in enumerate(all_categories):
        print(f"\n\n{'#'*60}")
        print(f"# 第 {i+1}/{len(all_categories)} 个 Category 探索")
        print(f"{'#'*60}")
        
        synthesized_program, _ = _explore_single_category(selected_category, all_categories)
        
        # 保存程序记忆到磁盘
        memory.save_to_disk()
        print(f"当前程序记忆: {memory.get_program_summary()}")

    return None


def explore_win_condition(non_clickable_objects, clickable_objects):
    """探索通关条件"""
    # 获取所有categories
    all_categories = [category_1, category_2, category_3, category_4]
    
    # 只在开始时重置一次画面
    print("=== 重置游戏画面到初始状态 ===")
    obs = env.reset()
    
    # 循环点击可点击物体，限定最大尝试次数
    for attempt in range(MAX_WIN_ATTEMPTS):
        # 从可点击物体中随机选择一个
        target_object_id = random.choice(clickable_objects)
        
        # 查找该object所在的category和详细信息
        selected_object = None
        category_index = None
        for cat_idx, category in enumerate(all_categories):
            for obj in category:
                if obj["id"] == target_object_id:
                    selected_object = obj
                    category_index = cat_idx + 1  # 编号从1开始
                    break
            if selected_object:
                break
        
        if not selected_object:
            continue
        
        # 从该object的网格坐标中随机选择一个
        grid_coordinates = selected_object["grid_coordinates"]
        selected_grid = random.choice(grid_coordinates)
        click_x, click_y = selected_grid
        
        # 获取当前画面并保存 - 通关尝试阶段
        frame_before = obs.frame
        add_video_frame(frame_before, click_pos=(click_x, click_y), category_index=category_index, 
                        object_id=target_object_id, frame_type='before', phase='win_attempt', 
                        attempt_num=attempt+1)
        time.sleep(CLICK_DELAY)
        
        # 在游戏画面中点击该网格
        print(f"尝试 {attempt+1}/20: 点击 Category {category_index} Object {target_object_id} 的网格 ({click_x}, {click_y})")
        result = env.step(action=6, data={'x': click_x, 'y': click_y})
        
        # 更新obs为当前状态（不重置）
        obs = result
        
        # 获取点击后画面并保存 - 通关尝试阶段
        frame_after = result.frame
        add_video_frame(frame_after, click_pos=(click_x, click_y), category_index=category_index, 
                        object_id=target_object_id, frame_type='after', phase='win_attempt', 
                        attempt_num=attempt+1)
        time.sleep(CLICK_DELAY)
        
        # 检查游戏状态
        if hasattr(result, 'done') and result.done:
            print(f"游戏通关！点击 Category {category_index} Object {target_object_id} 后完成")
            return True
    
    return False


def classify_objects_by_effect():
    """
    将物体分类为不可点击和可点击两类
    
    Returns:
        Tuple[List[int], List[int]]: (不可点击物体ID列表, 可点击物体ID列表)
    """
    non_clickable = []  # lambda $0，点击无效果
    clickable = []      # 有实际效果的程序
    
    # 使用策略进行效果分类（可自定义）
    effect_classification_strategy = ACTIVE_STRATEGIES['effect_classification']
    
    # 遍历程序库中的所有 object_id
    for object_id, programs in memory.program_library.programs.items():
        has_effect = False
        for program_info in programs:
            program_str = program_info.get("program", "")
            # 使用策略判断效果类型
            effect_type = effect_classification_strategy(program_str)
            if effect_type == 'no_effect':
                has_effect = False
                break
            elif effect_type == 'has_effect':
                has_effect = True
                break
        
        if has_effect:
            clickable.append(object_id)
        else:
            non_clickable.append(object_id)
    
    # 排序
    non_clickable.sort()
    clickable.sort()
    
    return non_clickable, clickable


if __name__ == "__main__":
    print("="*60)
    print("Alpha AI - 好奇心探索系统")
    print("="*60)
    
    # 初始化视频录制
    init_video_recorder()

    # 加载程序记忆
    if USE_LONG_TERM_MEMORY:
        memory.load_from_disk()
        print(f"初始程序记忆: {memory.get_program_summary()}")
    else:
        print("长期记忆已禁用")

    # 遍历所有category进行探索
    if ENABLE_EXPLORATION:
        curiosity_exploration()
        print(f"\n所有Category探索完成！")
        print(f"最终程序记忆: {memory.get_program_summary()}")
    else:
        print("探索阶段已跳过")

    # 分类物体
    non_clickable, clickable = classify_objects_by_effect()
    print(f"\n不可点击物体: {non_clickable}")
    print(f"可点击物体: {clickable}")

    # 探索通关条件
    win_result = False
    if ENABLE_WIN_ATTEMPT:
        print("\n开始探索通关条件...")
        win_result = explore_win_condition(non_clickable, clickable)
    else:
        print("\n通关尝试已跳过")

    # 释放视频录制器
    release_video_recorder()

    # 清空程序记忆（可选）
    if CLEAR_MEMORY_AFTER_RUN:
        memory.clear_all_memory()
        memory.save_to_disk()
        print("\n程序记忆已清空")
    else:
        memory.save_to_disk()
        print("\n程序记忆已保存")

    if win_result:
        print("\n通关成功！")
    else:
        print("\n未能通关")
