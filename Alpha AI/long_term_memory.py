"""
长期记忆库 (Long-Term Memory)
用于存储和管理AI的程序记忆数据

记忆结构:
- procedural_memory: 程序记忆（如何做事情）
- program_library: 存储合成过的程序（object_id → programs）
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class ProgramLibrary:
    """
    程序库类 - 存储DreamCoder合成的程序
    """
    
    def __init__(self):
        self.programs: Dict[int, List[Dict]] = {}  # object_id -> [program_info]
    
    def add_program(self, object_id: int, program_str: str, input_matrix: List, 
                   output_matrix: List, mdl: float):
        """
        添加程序到库中
        
        Args:
            object_id: 对象ID
            program_str: 程序字符串
            input_matrix: 输入矩阵
            output_matrix: 输出矩阵
            mdl: MDL值
        """
        if object_id not in self.programs:
            self.programs[object_id] = []
        
        program_info = {
            "program": program_str,
            "input": input_matrix,
            "output": output_matrix,
            "mdl": mdl,
            "learned_at": datetime.now().isoformat(),
            "use_count": 0
        }
        
        # 检查是否已存在相同程序
        for existing in self.programs[object_id]:
            if existing["program"] == program_str:
                existing["use_count"] += 1
                return
        
        self.programs[object_id].append(program_info)
    
    def get_programs(self, object_id: int) -> List[Dict]:
        """获取某个object_id的所有程序"""
        return self.programs.get(object_id, [])
    
    def has_exact_match(self, object_id: int, input_matrix: List, 
                       output_matrix: List) -> Optional[str]:
        """
        检查是否有完全匹配的已学过程序
        
        Args:
            object_id: 对象ID
            input_matrix: 输入矩阵
            output_matrix: 输出矩阵
            
        Returns:
            匹配的程序字符串，如果没有匹配返回None
        """
        programs = self.get_programs(object_id)
        for p in programs:
            if p["input"] == input_matrix and p["output"] == output_matrix:
                p["use_count"] += 1
                return p["program"]
        return None
    
    def save(self, filepath: str):
        """保存程序库到文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.programs, f, ensure_ascii=False, indent=2)
    
    def load(self, filepath: str) -> bool:
        """从文件加载程序库"""
        if not os.path.exists(filepath):
            return False
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # JSON加载后键是字符串，需要转换为整数
            self.programs = {int(k): v for k, v in data.items()}
        return True
    
    def summary(self) -> str:
        """生成程序库摘要"""
        total = sum(len(progs) for progs in self.programs.values())
        return f"程序库: {total}个程序, {len(self.programs)}个object_id"


class LongTermMemory:
    """
    长期记忆库类
    提供程序记忆的存储、检索、更新和管理功能
    """
    
    def __init__(self, storage_path: str = "memory"):
        """
        初始化记忆库
        
        Args:
            storage_path: 记忆数据存储目录
        """
        self.storage_path = storage_path
        self._initialize_storage()
        
        # 程序记忆
        self.procedural_memory: Dict[str, Any] = {}
        
        # DreamCoder程序库
        self.program_library = ProgramLibrary()
        
        # 元数据
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    def _initialize_storage(self):
        """初始化存储目录"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def add_procedural_memory(self, task: str, steps: List[str]):
        """
        添加程序记忆（操作步骤）
        
        Args:
            task: 任务名称
            steps: 操作步骤列表
        """
        self.procedural_memory[task] = {
            "steps": steps,
            "added_at": datetime.now().isoformat(),
            "last_used": None
        }
        self.metadata["last_updated"] = datetime.now().isoformat()
    
    def retrieve_procedural_memory(self, task: str) -> Optional[List[str]]:
        """
        检索程序记忆
        
        Args:
            task: 任务名称
            
        Returns:
            操作步骤列表，如果不存在返回None
        """
        if task in self.procedural_memory:
            self.procedural_memory[task]["last_used"] = datetime.now().isoformat()
            return self.procedural_memory[task]["steps"]
        return None
    
    def store_synthesized_program(self, object_id: int, program_str: str, 
                                  input_matrix, output_matrix, mdl: float):
        """
        存储合成的程序到记忆库
        
        Args:
            object_id: 对象ID
            program_str: 程序字符串
            input_matrix: 输入矩阵
            output_matrix: 输出矩阵
            mdl: MDL值
        """
        input_list = input_matrix.tolist() if hasattr(input_matrix, 'tolist') else input_matrix
        output_list = output_matrix.tolist() if hasattr(output_matrix, 'tolist') else output_matrix
        
        self.program_library.add_program(object_id, program_str, input_list, output_list, mdl)
        self.metadata["last_updated"] = datetime.now().isoformat()
    
    def retrieve_synthesized_program(self, object_id: int, input_matrix, 
                                    output_matrix) -> Optional[str]:
        """
        检索已学过的程序
        
        Args:
            object_id: 对象ID
            input_matrix: 输入矩阵
            output_matrix: 输出矩阵
            
        Returns:
            程序字符串，如果不存在返回None
        """
        input_list = input_matrix.tolist() if hasattr(input_matrix, 'tolist') else input_matrix
        output_list = output_matrix.tolist() if hasattr(output_matrix, 'tolist') else output_matrix
        
        return self.program_library.has_exact_match(object_id, input_list, output_list)
    
    def save_to_disk(self, filename: str = "memory.json"):
        """
        将记忆库保存到磁盘
        
        Args:
            filename: 保存的文件名
        """
        # 保存程序记忆
        procedural_data = {
            "metadata": self.metadata,
            "procedural_memory": self.procedural_memory
        }
        procedural_filepath = os.path.join(self.storage_path, filename)
        with open(procedural_filepath, "w", encoding="utf-8") as f:
            json.dump(procedural_data, f, ensure_ascii=False, indent=2)
        
        # 保存程序库
        library_filepath = os.path.join(self.storage_path, "program_library.json")
        self.program_library.save(library_filepath)
        
        print(f"Memory saved to {procedural_filepath}")
        print(f"Program library saved to {library_filepath}")
    
    def load_from_disk(self, procedural_filename: str = "memory.json",
                       library_filename: str = "program_library.json") -> bool:
        """
        从磁盘加载记忆库
        
        Args:
            procedural_filename: 程序记忆文件名
            library_filename: 程序库文件名
            
        Returns:
            是否加载成功
        """
        # 加载程序记忆
        procedural_filepath = os.path.join(self.storage_path, procedural_filename)
        if os.path.exists(procedural_filepath):
            with open(procedural_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.metadata = data.get("metadata", self.metadata)
            self.procedural_memory = data.get("procedural_memory", {})
        
        # 加载程序库
        library_filepath = os.path.join(self.storage_path, library_filename)
        if self.program_library.load(library_filepath):
            print(f"Program library loaded from {library_filepath}")
        
        return True
    
    def clear_all_memory(self):
        """清空所有记忆"""
        self.procedural_memory = {}
        self.program_library = ProgramLibrary()
        self.metadata["last_updated"] = datetime.now().isoformat()
        print("All memory cleared")
    
    def get_program_summary(self) -> str:
        """获取程序库摘要"""
        return self.program_library.summary()


# 创建全局记忆库实例
memory = LongTermMemory()