# tool/base.py
class Tool:
    _tools = {}  # 工具注册表
    _descriptions = {}  # 工具描述注册表

    def __init__(self, name: str):
        self.name = name

        self._active = False

    @classmethod
    def register(cls, name):
        def wrapper(tool_cls):
            cls._tools[name] = tool_cls

            return tool_cls
        return wrapper
    
    @classmethod
    def create(cls, name, *args, **kwargs):
        if name not in cls._tools:
            raise ValueError(f"Tool '{name}'没有被注册")
        return cls._tools[name](*args, **kwargs)

    def use(self, *args, **kwargs):
        self._active = True
        try:
            return self._execute(*args, **kwargs)
        finally:
            self._active = False

    def _execute(self, *args, **kwargs):
        raise NotImplementedError("子类必须实现此方法")

    @property
    def is_active(self):
        return self._active