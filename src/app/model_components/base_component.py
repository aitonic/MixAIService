from abc import ABC, abstractmethod


class BaseComponent:
    """Base component.
    
    All components must inherit from this base class.
    """

    def __init__(self, name: str = None) -> None:
        # If polymorphism or other parent class calls are needed, 
        # you can use super().__init__(), but keep it simple here.
        self.name = name
        # Common initialization logic can be written here.

    def as_parameter(self) -> "BaseComponent":
        # This method is used to return the current component as a parameter,
        # making it convenient for other components to use.
        # By calling this method, users can obtain an instance of the current component.
        return self


class BaseFactory(ABC):
    """Base factory class.
    
    This is the base class for all factories. 
    All component factories *must* implement this base class.
    The `get_bean` method is the only entry point for obtaining a corresponding component.
    Factories that do not implement this base class will not be managed by the service container!
    """

    def check(self, param: dict) -> None:
        if "component_type" not in param:
            raise Exception("component_type must be specified")
        
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
    def get_bean(self, param: dict) -> BaseComponent:
        """Get the bean instance.
        
        This is the only way to get a bean using the factory.
        You can define whether it's singleton or polymorphic, or any other special attributes.
        
        Args:
            param (dict): Parameters for creating the bean
            
        Returns:
            BaseComponent: The created bean instance
        """
        pass
