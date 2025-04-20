import re
from .base_tool import Tool
from typing import Union
import operator

class Calculator(Tool):
    """计算器工具，支持基本数学运算和表达式解析"""
    
    def __init__(self):
        super().__init__(name="calculator")
        # 支持的运算符映射
        self.operations = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '^': operator.pow,
            'add': operator.add,
            'subtract': operator.sub,
            'multiply': operator.mul,
            'divide': operator.truediv,
            'power': operator.pow
        }

    def _execute(self, *args, **kwargs) -> Union[float, int]:
        """
        执行计算操作
        
        支持多种输入格式:
        - 表达式字符串: "5+3"
        - 直接参数: (5, '+', 3)
        - 字典参数: {'numbers': [5, 3], 'operation': '+'}
        - 关键字参数: num1=5, num2=3, operation='+'
        """
        # 如果是单个字符串参数，尝试解析为表达式
        if len(args) == 1 and isinstance(args[0], str) and not kwargs:
            return self._evaluate_expression(args[0])
            
        # 否则按原逻辑处理
        numbers, operation = self._parse_arguments(*args, **kwargs)
        return self._compute(numbers, operation)

    def _evaluate_expression(self, expr: str) -> Union[float, int]:
        """计算数学表达式"""
        # 移除所有空白字符
        expr = re.sub(r'\s+', '', expr)
        
        # 使用正则表达式匹配数字和运算符
        pattern = r'([-+]?\d*\.?\d+)([-+*/^])([-+]?\d*\.?\d+)'
        match = re.fullmatch(pattern, expr)
        
        if not match:
            raise ValueError(f"无效的数学表达式: {expr}")
            
        num1, op, num2 = match.groups()
        
        try:
            num1 = float(num1) if '.' in num1 else int(num1)
            num2 = float(num2) if '.' in num2 else int(num2)
        except ValueError:
            raise ValueError("表达式包含无效数字")
            
        return self._compute([num1, num2], op)

    def _compute(self, numbers: list, operation: str) -> Union[float, int]:
        """执行实际计算"""
        if operation not in self.operations:
            raise ValueError(f"不支持的操作: {operation}")
            
        try:
            result = numbers[0]
            for num in numbers[1:]:
                result = self.operations[operation](result, num)
            return result
        except ZeroDivisionError:
            raise ZeroDivisionError("不能除以零")
        except Exception as e:
            raise ValueError(f"计算错误: {str(e)}")

    def _parse_arguments(self, *args, **kwargs):
        """解析非表达式形式的参数"""
        # 原解析逻辑保持不变
        if args and isinstance(args[0], dict):
            params = args[0]
            numbers = params.get('numbers', [])
            operation = params.get('operation', '+')
        elif kwargs:
            numbers = [v for k, v in kwargs.items() if k.startswith('num')]
            operation = kwargs.get('operation', '+')
        elif len(args) >= 3 and isinstance(args[1], str):
            numbers = [args[0], args[2]]
            operation = args[1]
            if len(args) > 3:
                numbers.extend(args[3:])
        else:
            raise ValueError("无效的计算参数")
            
        if not numbers:
            raise ValueError("必须提供至少一个数字")
            
        try:
            numbers = [float(n) if '.' in str(n) else int(n) for n in numbers]
        except ValueError:
            raise ValueError("无效的数字格式")
            
        return numbers, str(operation)