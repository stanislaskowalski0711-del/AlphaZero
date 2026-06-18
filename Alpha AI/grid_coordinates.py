GRID_TOP_LEFT_X = 0
GRID_TOP_LEFT_Y = 0
GRID_ORIGIN = (GRID_TOP_LEFT_X, GRID_TOP_LEFT_Y)

X_AXIS_DIRECTION = "RIGHT"
Y_AXIS_DIRECTION = "DOWN"

def get_grid_coordinate(relative_x: int, relative_y: int) -> tuple[int, int]:
    """
    以网格为单位计算坐标
    - relative_x: 相对于原点向右的网格数
    - relative_y: 相对于原点向下的网格数
    例如：原点正下方相邻网格为 get_grid_coordinate(0, 1) -> (0, 1)
    """
    return (GRID_TOP_LEFT_X + relative_x, GRID_TOP_LEFT_Y + relative_y)