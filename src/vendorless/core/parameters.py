
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
    _ALL_BLUEPRINT_PARAMETERS: list[weakref.ReferenceType['ConfigurationParameter']] = []

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = value
        for ref in self._dependants:
            ref.param.__set__(ref.obj, value)

    # blueprint parameters should be documented in docs, not a description attribute

    def __init__(self, *keys: str, default=INFER, type: type=str, choices: list[str]=None) -> None:
        self.keys: tuple[str, ...] = keys
        self.default = default
        self.choices = choices
        self.type = type
        ConfigurationParameter._ALL_BLUEPRINT_PARAMETERS.append(weakref.ref(self))
        self._dependants: list[ParameterReference] = []
        self.value = UNRESOLVED if default is INFER else default

    
    def register_dependant(self, reference: ParameterReference):
        if self.default is INFER and reference.param.default is not UNRESOLVED:
            if self.value != UNRESOLVED and self.value != reference.param.default:
                warnings.warn(
                    f"Blueprint parameter '{self.keys}' is inferring a default value from parameters with different values."
                    f"Previous default value: {self.value}. New default value: {reference.param.default}."
                )
            self.value = reference.param.default
        self._dependants.append(reference)
        reference.param.__set__(reference.obj, self.value)
    
    @classmethod
    def resolve(
        cls, 
        console: Console,
        conf: pathlib.Path | None = None,
        root_element: str=None
    ):
        settings = {}
        if conf:
            with open(conf, 'r') as f:
                console.print(f"Loading settings from [bold]{f.name}[/bold]")
                s = yaml.safe_load(f)
                if root_element:
                    settings = s[root_element]
                else:
                    settings = s
        
        def setting_exists(keys: tuple[str, ...], settings: dict):
            s = settings
            for k in keys:
                if (k not in s):
                    return False
                s = s[k]
            return True
        
        def get_setting(keys: tuple[str, ...], settings: dict):
            if len(keys) == 1:
                return settings[keys[0]]
            else:
                return get_setting(keys[1:], settings[keys[0]])  
        
        def set_setting(keys: tuple[str, ...], value, settings: dict):
            if len(keys) == 1:
                settings[keys[0]] = value
            else:
                if keys[0] not in settings:
                    settings[keys[0]] = {}
                set_setting(keys[1:], value, settings[keys[0]])
                  
        last_level: tuple[str, ...] = ()
        indent = 0

        for bp_wr in cls._ALL_BLUEPRINT_PARAMETERS:
            blueprint_parameter: ConfigurationParameter | None =  bp_wr()
            if blueprint_parameter is None:
                continue

            current_level: tuple[str, ...] = blueprint_parameter.keys[:-1]
            if current_level != last_level:
                start_level = next(
                    (i for i, (kc, kl) in enumerate(zip(current_level, last_level)) if kc != kl),
                    min(len(current_level), len(last_level))
                )
                for i in range(start_level, len(current_level)):
                    indent = i * 4
                    console.print(f"{' '*indent}[cyan]{current_level[i]}[/cyan]:")
                
            indent = len(current_level) * 4

            if setting_exists(blueprint_parameter.keys, settings):
                s = get_setting(blueprint_parameter.keys, settings)
                s = blueprint_parameter.type(s)
                console.print(f"{' '*indent}[cyan]{blueprint_parameter.keys[-1]}[/cyan]: {s}")
            else:
                s = ""
                while isinstance(s, str) and len(s) == 0:
                    kwargs = {}
                    default = blueprint_parameter.value
                    if default is UNRESOLVED:
                        default = None
                    else:
                        kwargs['default'] = default

                    s = Prompt.ask(
                        f"{' '*indent}[cyan bold]{blueprint_parameter.keys[-1]}[/cyan bold]",
                        console=console,
                        **kwargs,
                        choices=blueprint_parameter.choices,
                    )
                
                s = blueprint_parameter.type(s)
                set_setting(blueprint_parameter.keys, s, settings)
            
            blueprint_parameter.value = s
        
        with open('vendorless.yaml', 'w') as f:
            yaml.safe_dump(settings, f)

            
def configuration_parameter(*keys: str, default=INFER, type: type=str, choices: list[str]=None):
    for c in ConfigurationParameter._ALL_BLUEPRINT_PARAMETERS:
        c : None | ConfigurationParameter = c()
        if c is None or c.keys != keys:
            continue
        return c
    return ConfigurationParameter(*keys, default=default, type=type, choices=choices)


         
