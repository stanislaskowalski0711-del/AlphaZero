"""
ARC-AGI-3 画面和矩阵保存模块
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ARC-AGI-3 Correct Color Mapping
COLOR_MAP = {
    0: (255, 255, 255),  # White
    1: (204, 204, 204),  # Off-white
    2: (153, 153, 153),  # neutral Light
    3: (102, 102, 102),  # neutral
    4: (51, 51, 51),     # Off Black
    5: (0, 0, 0),        # Black
    6: (229, 58, 163),   # Magenta
    7: (255, 123, 204),  # Magenta Light
    8: (249, 60, 49),    # Red
    9: (30, 147, 255),   # Blue
    10: (136, 216, 241), # Blue Light
    11: (255, 220, 0),   # Yellow
    12: (255, 133, 27),  # Orange
    13: (146, 18, 49),   # Maroon
    14: (79, 204, 48),   # Green
    15: (163, 86, 214),  # Purple
}


def save_frame_with_grid(frame_array, filename, click_pos=None):
    """保存带网格的游戏画面"""
    # 将颜色索引转换为RGB数组
    height, width = frame_array.shape
    rgb_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    for y in range(height):
        for x in range(width):
            value = int(frame_array[y, x])
            rgb_array[y, x] = COLOR_MAP.get(value, (0, 0, 0))
    
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_aspect('equal')
    ax.invert_yaxis()
    ax.set_xlim(-0.5, 63.5)
    ax.set_ylim(63.5, -0.5)
    ax.axis('off')
    
    ax.imshow(rgb_array, interpolation='nearest')
    
    # 绘制网格
    for i in range(65):
        ax.axvline(i - 0.5, color='gray', linewidth=0.3)
        ax.axhline(i - 0.5, color='gray', linewidth=0.3)
    
    # 高亮点击位置
    if click_pos:
        x, y = click_pos
        rect = patches.Rectangle(
            (x - 0.5, y - 0.5),
            1, 1,
            linewidth=3,
            edgecolor='yellow',
            facecolor='none'
        )
        ax.add_patch(rect)
        ax.text(x, y - 1, f'({x},{y})', ha='center', va='bottom', 
                color='yellow', fontsize=10, fontweight='bold')
    
    plt.tight_layout(pad=0)
    plt.savefig(filename, dpi=100, bbox_inches='tight')
    plt.close(fig)


def save_object_matrix(matrix, filename, object_id, grid_coordinates, click_x, click_y, label):
    """保存object矩阵为可读的txt文件"""
    with open(filename, "w") as f:
        f.write(f"Object ID: {object_id}\n")
        f.write(f"Grid Coordinates: {grid_coordinates}\n")
        f.write(f"Click Position: ({click_x}, {click_y})\n")
        f.write(f"Object Matrix ({label}):\n")
        for row in matrix:
            f.write("  " + " ".join(str(v) for v in row) + "\n")


def extract_object_matrix(frame_matrix, grid_coordinates):
    """从画面矩阵中提取object区域的矩阵"""
    object_matrix = np.zeros((6, 6), dtype=np.int32)
    for i, (gx, gy) in enumerate(grid_coordinates):
        row = i // 6
        col = i % 6
        object_matrix[row, col] = frame_matrix[gy, gx]
    return object_matrix


def convert_frame_to_matrix(frame_data):
    """将frame数据转换为numpy矩阵"""
    if isinstance(frame_data, list) and len(frame_data) > 0:
        frame_array = frame_data[0]
    else:
        frame_array = frame_data
    
    if frame_array.ndim == 3 and frame_array.shape[0] == 1:
        frame_array = frame_array.squeeze(0)
    
    return np.array(frame_array)