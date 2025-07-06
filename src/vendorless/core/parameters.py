
from dataclasses import dataclass
import warnings

import inspect
from typing import Any
import pathlib
import rich
import yaml
import weakref

from rich.console import Console
from rich.prompt import Prompt

console = Console()


@dataclass
class ParameterReference:
    obj: object
    param: Any

    def dereference(self):
        return self.param.__get__(self.obj, self.obj.__class__)

UNRESOLVED = object()

class Parameter:
    def __init__(self, default=UNRESOLVED) -> None:
        self.default = default

    def __set_name__(self, owner, name):
        self.attr_name = f'_{name}'

    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        is_resolved = hasattr(instance, self.attr_name) and not isinstance(instance, ParameterReference)

        if not is_resolved:
            return ParameterReference(instance, self)
        
        value = getattr(instance, self.attr_name)
        if isinstance(value, ParameterReference):
            value = value.dereference()

        return value
    
    def __set__(self, instance, value):
        if value is self:
            value = self.default
        
        if isinstance(value, ConfigurationParameter):
            value.register_dependant(ParameterReference(instance, self))
        elif value is not UNRESOLVED:
            setattr(instance, self.attr_name, value)
    
    def __repr__(self) -> str:
        return f"<parameter {self.attr_name}>"
    
def parameter(default=UNRESOLVED) -> Any:
    return Parameter(default)

class computed_parameter: # pylint: disable=invalid-name
    def __init__(self, func):
        self.func = func
        self.attr_name = f"_{func.__name__}"

        sig = inspect.signature(func)

        self.precursors = [
            name for name, param in sig.parameters.items()
            if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]
        assert self.precursors[0] == 'self'
        self.precursors = self.precursors[1:]
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        args = list(getattr(instance, p) for p in self.precursors)
        if any(isinstance(a, ParameterReference) for a in args):
            return ParameterReference(instance, self)
        value = self.func(instance, *args)
        return value

INFER=object()


class ConfigurationParameter:
    _ALL_CONFIGURATION_PARAMETERS: list[weakref.ReferenceType['ConfigurationParameter']] = []

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = value
        for ref in self._connected_parameters:
            ref.param.__set__(ref.obj, value)

    # blueprint parameters should be documented in docs, not a description attribute

    def __init__(self, *keys: str, default=INFER, type: type=str, choices: list[str]=None) -> None:
        self.keys: tuple[str, ...] = keys
        self.default = default
        self.choices = choices
        self.type = type
        ConfigurationParameter._ALL_CONFIGURATION_PARAMETERS.append(weakref.ref(self))
        self._connected_parameters: list[ParameterReference] = []
        self.value = UNRESOLVED if default is INFER else default

    
    def register_dependant(self, reference: ParameterReference):
        if self.default is INFER and reference.param.default is not UNRESOLVED:
            if self.value != UNRESOLVED and self.value != reference.param.default:
                warnings.warn(
                    f"Configuration parameter '{self.keys}' is inferring a default value from parameters with different values."
                    f"Previous default value: {self.value}. New default value: {reference.param.default}."
                )
            self.value = reference.param.default
        self._connected_parameters.append(reference)
        reference.param.__set__(reference.obj, self.value)

class Configuration:
    INDENT = ' '*4

    def __init__(self, path: pathlib.Path | None, config_selector: str | None) -> 'Configuration':
        if path is None:
            self._config = {}
        else:
            console.print(f"Loading configuration from [bold]{str(path)}[/bold]")
            with open(path, 'r') as f:
                self._config = yaml.safe_load(f)
        
        if config_selector is not None:
            self._config = self.get(config_selector)
    
    def has(self, keys: tuple[str, ...], *, subset: dict | None = None):
        s = self._config if subset is None else subset
        if len(keys) == 1:
            return keys[0] in s
        elif keys[0] not in s:
            return False
        else:
            return self.has(keys[1:], subset=s[keys[0]]) 
    
    def get(self, keys: tuple[str, ...], *, subset: dict | None = None):
        s = self._config if subset is None else subset
        if len(keys) == 1:
            return s[keys[0]]
        else:
            return self.get(keys[1:], subset=s[keys[0]])  
    
    def set(self, keys: tuple[str, ...], value, *, subset: dict | None = None):
        s = self._config if subset is None else subset
        if len(keys) == 1:
            s[keys[0]] = value
        else:
            if keys[0] not in s:
                s[keys[0]] = {}
            self.set(keys[1:], value, subset=s[keys[0]])

    @classmethod
    def print_scope(cls, indent_level: int, key: str):
        s = f"{cls.INDENT*indent_level}[cyan]{key}[/cyan]:"
        console.print(s)

    @classmethod
    def print_setting(cls, indent_level: int, key: str, value):
        s = f"{cls.INDENT*indent_level}[cyan]{key}[/cyan]: {value}"
        console.print(s)
        
    @classmethod
    def prompt_setting(cls, indent_level: int, configuration_parameter: ConfigurationParameter) -> Any:
        s = ""
        while isinstance(s, str) and len(s) == 0:
            kwargs = {}
            default = configuration_parameter.value
            if default is UNRESOLVED:
                default = None
            else:
                kwargs['default'] = default

            s = Prompt.ask(
                f"{cls.INDENT*indent_level}[cyan bold]{configuration_parameter.keys[-1]}[/cyan bold]",
                console=console,
                **kwargs,
                choices=configuration_parameter.choices,
            )
            try:
                s = configuration_parameter.type(s)
            except ValueError:
                console.print(f"[red bold]Error[/bold]: You must enter a {str(configuration_parameter.type)} (invalid entry: '{s}').[/red]")
        return s

    def resolve(self):
        console.print("Resolving configuration")           
        last_level: tuple[str, ...] = ()
        indent = 0

        for configuration_parameter_wr in ConfigurationParameter._ALL_CONFIGURATION_PARAMETERS:
            configuration_parameter: ConfigurationParameter | None =  configuration_parameter_wr()
            if configuration_parameter is None:
                continue

            current_level: tuple[str, ...] = configuration_parameter.keys[:-1]
            if current_level != last_level:
                start_level = next(
                    (i for i, (kc, kl) in enumerate(zip(current_level, last_level)) if kc != kl),
                    min(len(current_level), len(last_level))
                )
                for i in range(start_level, len(current_level)):
                    self.print_scope(i, current_level[i])
                
            indent = len(current_level)

            if self.has(configuration_parameter.keys):
                s = self.get(configuration_parameter.keys)
                s = configuration_parameter.type(s)
                self.print_setting(indent, configuration_parameter.keys[-1], s)
            else:
                s = self.prompt_setting(indent, configuration_parameter)
                self.set(configuration_parameter.keys, s)
            
            configuration_parameter.value = s
    
    def dict(self) -> dict:
        return self._config

            
def configuration_parameter(*keys: str, default=INFER, type: type=str, choices: list[str]=None):
    for c in ConfigurationParameter._ALL_CONFIGURATION_PARAMETERS:
        c : None | ConfigurationParameter = c()
        if c is None or c.keys != keys:
            continue
        return c
    return ConfigurationParameter(*keys, default=default, type=type, choices=choices)


         
