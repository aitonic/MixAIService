from abc import ABC, abstractmethod

class BaseComponent:
    """基础组件。
    
    所有的组件，都需要继承自这个组件。
    """

    def __init__(self, name: str = None) -> None:
    # 如果还需要多态或其他父类调用，可使用 super().__init__()，但此处最简单即可
        self.name = name
    # 这里可以写一些共同的初始化逻辑

    def as_parameter(self) -> "BaseComponent":
        # 该方法用于将当前组件作为参数返回，方便其他组件使用。
        # 通过调用此方法，用户可以获取到当前组件的实例。
        return self


class BaseFactory(ABC):
    """Base factory class.
    
    The base class for all factories. All component factories *must* implement this class.
    get_bean is the only entry point to get corresponding components.
    Factories that do not implement this base class will not be managed by the service container!
    """

    def check(self, param:dict) -> None:
        if "component_type" not in param:
            raise Exception(f"component_type must be specified")
        
    def get_component(self, param:dict) -> BaseComponent:
        """Get component instance through factory.
        
        This method will first check the parameters and then call get_bean to create the component.
        
        Args:
            param (dict): Parameters for creating the component, must contain 'component_type'
            
        Returns:
            BaseComponent: The created component instance
        """
        self.check(param)
        return self.get_bean(param)

    @abstractmethod
    def get_bean(self, param:dict) -> BaseComponent:
        """Get bean instance.
        
        This is the only way to get bean through factory.
        You can define whether it's singleton or polymorphic, or any other special attributes.
        
        Args:
            param (dict): Parameters for creating the bean
            
        Returns:
            BaseComponent: The created bean instance
        """
        pass