import os
from pathlib import Path
import json
from typing import List, Dict, Any, Optional


class Memory:
    def __init__(self, path: str = "/memory/history.json"):
        """
        初始化 Memory 类，用于管理对话历史。
        Args:
            path (str): 历史记录存储的 JSON 文件路径。默认为 "history.json"。
        """
        self.history: List[Dict[str, Any]] = []
        self.path = path

    def save_history(self, item: Dict[str, Any]) -> None:
        """
        保存对话记录到 JSON 文件。
        
        Args:
            item (Dict[str, Any]): 要保存的对话记录（字典格式）。
        """
        self.history.append(item)
        
        # 确保目录存在
        directory = os.path.dirname(self.path)
        if directory:  # 如果路径包含目录（如 "data/history.json"）
            os.makedirs(directory, exist_ok=True)
        
        # 写入 JSON 文件
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(self.history, file, ensure_ascii=False, indent=2)

    def load_history(self) -> List[Dict[str, Any]]:
        """
        从 JSON 文件加载对话历史。
        
        Returns:
            List[Dict[str, Any]]: 加载的历史记录列表。如果文件不存在，返回空列表。
        """
        try:
            if os.path.exists(self.path):
                with open(self.path, 'r', encoding='utf-8') as file:
                    self.history = json.load(file)
            else:
                print(f"文件不存在: {self.path}")
                self.history = []
        except json.JSONDecodeError:
            print(f"文件格式错误: {self.path}")
            self.history = []
        return self.history

    def recall(self):
        return self.history
    
    def pop_history(self):
        return self.history.pop()
    def clear(self):
        self.history=[]
        