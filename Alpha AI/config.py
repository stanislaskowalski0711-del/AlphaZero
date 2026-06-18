"""
Alpha AI 配置文件
请根据需要修改以下参数，无需修改核心代码
"""

# ==================== 游戏配置 ====================
# 游戏名称 (支持的游戏: ft09)
GAME_NAME = "ft09"

# API Key (需要从ARC-AGI平台获取)
ARC_API_KEY = "32cb5324-578b-4c55-88e9-03004953cb1b"

# ==================== 探索阶段配置 ====================
# 是否启用探索阶段
ENABLE_EXPLORATION = True

# 每个category选择多少个代表object进行探索
OBJECTS_PER_CATEGORY = 1

# 探索间隔时间（秒）
EXPLORATION_DELAY = 2

# ==================== 程序合成配置 ====================
# 程序合成超时时间（秒）
SYNTHESIS_TIMEOUT = 120

# 最大程序深度
MAX_PROGRAM_DEPTH = 3

# ==================== 通关尝试配置 ====================
# 是否启用通关尝试
ENABLE_WIN_ATTEMPT = True

# 最大尝试次数
MAX_WIN_ATTEMPTS = 50

# 点击间隔时间（秒）
CLICK_DELAY = 2

# 是否避免重复点击同一网格
AVOID_DUPLICATE_CLICKS = True

# ==================== 视频录制配置 ====================
# 是否录制视频
ENABLE_VIDEO_RECORDING = True

# 视频帧率（fps）
VIDEO_FPS = 1

# 视频分辨率放大倍数（64 * SCALE_FACTOR）
SCALE_FACTOR = 16

# ==================== 记忆配置 ====================
# 是否使用长期记忆
USE_LONG_TERM_MEMORY = True

# 记忆文件路径
MEMORY_FILE_PATH = "memory/program_library.json"

# 是否在运行结束后清空记忆（用于演示时每次从头开始）
CLEAR_MEMORY_AFTER_RUN = False

# ==================== 日志配置 ====================
# 是否输出详细日志
VERBOSE_LOGGING = True

# 日志文件路径（None表示不保存到文件）
LOG_FILE_PATH = None

# ==================== 调试配置 ====================
# 是否启用调试模式（输出更多调试信息）
DEBUG_MODE = False
