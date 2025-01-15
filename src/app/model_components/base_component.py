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
    """基础的工厂类。
    所有工厂的基类，所有组件的工厂都*必须*实现这个组件。
    get_bean是唯一的获取对应组件的入口
    未实现该基类的工厂，将不被服务容器管理！
    """

    def check(self, param:dict) -> None:
        if "component_type" not in param:
            raise Exception(f"component_type must be specified")
        
    def get_component(self, param:dict) -> BaseComponent:
        self.check(param)
        return self.get_bean(param)

    @abstractmethod
    def get_bean(self, param:dict) -> BaseComponent:
        """获取bean实例。
        这个是使用工厂获取bean的唯一方式。
        至于是单例还是多态，或者是否有其他特殊属性，均可自行定义。
        """
        pass