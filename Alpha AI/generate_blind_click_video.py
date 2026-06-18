"""
盲目点击行为展示视频生成脚本
使用正确的ARC-AGI颜色映射
"""
import arc_agi
import os
import cv2
import numpy as np
import time
from datetime import datetime

os.environ["ARC_API_KEY"] = "32cb5324-578b-4c55-88e9-03004953cb1b"

# ARC-AGI-3 标准颜色映射
# 值范围: 0-15
COLOR_MAP = {
    0: (255, 255, 255),   # White - 白色背景
    1: (204, 204, 204),   # Light gray - 浅灰
    2: (153, 153, 153),   # Medium gray - 中灰
    3: (102, 102, 102),   # Dark gray - 深灰
    4: (51, 51, 51),      # Very dark gray - 近黑
    5: (0, 0, 0),         # Black - 黑色
    6: (229, 58, 163),    # Magenta - 品红
    7: (255, 123, 204),   # Light magenta - 浅品红
    8: (249, 60, 49),     # Red - 红色
    9: (30, 147, 255),    # Blue - 蓝色
    10: (136, 216, 241),  # Light blue - 浅蓝/青色
    11: (255, 220, 0),    # Yellow - 黄色
    12: (255, 133, 27),   # Orange - 橙色
    13: (146, 18, 49),    # Maroon - 栗色
    14: (79, 204, 48),    # Green - 绿色
    15: (163, 86, 214),   # Purple - 紫色
}

def get_grid_coordinate(x, y):
    return (x, y)

def convert_frame_to_rgb(frame_data):
    if isinstance(frame_data, list) and len(frame_data) > 0:
        frame_data = frame_data[0]
    
    if isinstance(frame_data, list):
        frame_data = np.array(frame_data)
    
    if not isinstance(frame_data, np.ndarray):
        return None
    
    if frame_data.ndim == 3 and frame_data.shape[0] == 1:
        frame_data = frame_data.squeeze(0)
    elif frame_data.ndim == 3 and frame_data.shape[0] > 1:
        frame_data = frame_data[0]

    height, width = frame_data.shape
    rgb_array = np.zeros((height, width, 3), dtype=np.uint8)

    for i in range(height):
        for j in range(width):
            color_idx = int(frame_data[i, j])
            if color_idx in COLOR_MAP:
                rgb_array[i, j] = COLOR_MAP[color_idx]
            else:
                rgb_array[i, j] = (128, 128, 128)

    return rgb_array

def add_grid_to_image(image, scale=16):
    large_image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    grid_color = (180, 180, 180)
    
    for i in range(0, large_image.shape[1] + 1, scale):
        cv2.line(large_image, (i, 0), (i, large_image.shape[0]), grid_color, 1)
    for i in range(0, large_image.shape[0] + 1, scale):
        cv2.line(large_image, (0, i), (large_image.shape[1], i), grid_color, 1)

    return large_image

def add_click_marker(image, pos, scale=16):
    x, y = pos
    x_scaled = x * scale
    y_scaled = y * scale
    top_left = (x_scaled, y_scaled)
    bottom_right = (x_scaled + scale, y_scaled + scale)
    cv2.rectangle(image, top_left, bottom_right, (0, 255, 255), 3)
    return image

def main():
    print("=" * 60)
    print("盲目点击行为展示视频生成")
    print("使用正确的ARC-AGI颜色映射")
    print("=" * 60)

    arc = arc_agi.Arcade()
    env = arc.make("ft09")
    obs = env.reset()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = f"blind_clicking_{timestamp}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 1
    frame_size = (1024, 1024)
    video_writer = cv2.VideoWriter(video_path, fourcc, fps, frame_size)

    import sys
    sys.path.insert(0, r"c:\Users\MR\Documents\trae_projects\Alpha AI")
    from categories import category_1, category_2, category_3, category_4

    all_categories = [category_1, category_2, category_3, category_4]
    all_grid_coords = []
    for category in all_categories:
        for obj in category:
            all_grid_coords.extend(obj["grid_coordinates"])

    print(f"总共有 {len(all_grid_coords)} 个可点击网格坐标")

    np.random.seed(42)
    shuffled_coords = all_grid_coords.copy()
    np.random.shuffle(shuffled_coords)

    total_clicks = 120
    print(f"\n开始录制 {total_clicks} 次盲目点击...")
    print("=" * 60)

    for i in range(total_clicks):
        obs = env.reset()

        if i < len(shuffled_coords):
            coord = shuffled_coords[i]
        else:
            coord = shuffled_coords[np.random.randint(0, len(shuffled_coords))]

        x, y = coord
        click_x, click_y = get_grid_coordinate(x, y)

        frame_before = obs.frame
        rgb_before = convert_frame_to_rgb(frame_before)
        
        if rgb_before is None:
            print(f"警告: 无法转换帧 {i+1}")
            continue

        display_frame = add_grid_to_image(rgb_before.copy())
        display_frame = add_click_marker(display_frame, (click_x, click_y))
        video_writer.write(display_frame)
        print(f"[{i+1}/{total_clicks}] 点击 ({click_x}, {click_y})")

        result = env.step(action=6, data={'x': click_x, 'y': click_y})

        frame_after = result.frame
        rgb_after = convert_frame_to_rgb(frame_after)
        
        if rgb_after is None:
            rgb_after = rgb_before

        display_after = add_grid_to_image(rgb_after.copy())
        display_after = add_click_marker(display_after, (click_x, click_y))
        video_writer.write(display_after)

        time.sleep(0.1)

        if (i + 1) % 10 == 0:
            print(f"  进度: {i+1}/{total_clicks}")

    video_writer.release()

    print("\n" + "=" * 60)
    print("视频录制完成！")
    print(f"保存路径: {video_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
