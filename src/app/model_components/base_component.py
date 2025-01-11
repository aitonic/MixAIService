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
