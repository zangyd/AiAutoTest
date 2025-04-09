"""
单例模式工具模块
"""
from typing import Dict, Any, Type, TypeVar

T = TypeVar('T')

class Singleton(type):
    """
    单例元类
    
    使用方法:
    ```python
    class MyClass(metaclass=Singleton):
        pass
    ```
    """
    
    _instances: Dict[Type, Any] = {}
    
    def __call__(cls, *args, **kwargs):
        """
        创建或返回单例实例
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Any: 单例实例
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
    
    @classmethod
    def clear_instance(mcs, cls: Type[T]) -> None:
        """
        清除指定类的单例实例
        
        Args:
            cls: 要清除实例的类
        """
        if cls in mcs._instances:
            del mcs._instances[cls]
    
    @classmethod
    def has_instance(mcs, cls: Type[T]) -> bool:
        """
        检查指定类是否已创建单例实例
        
        Args:
            cls: 要检查的类
            
        Returns:
            bool: 如果已创建实例返回True，否则返回False
        """
        return cls in mcs._instances
    
    @classmethod
    def get_instance(mcs, cls: Type[T]) -> T:
        """
        获取指定类的单例实例
        
        Args:
            cls: 要获取实例的类
            
        Returns:
            T: 单例实例
            
        Raises:
            KeyError: 如果实例不存在
        """
        if cls not in mcs._instances:
            raise KeyError(f"No instance found for class {cls.__name__}")
        return mcs._instances[cls] 