from mypy.plugin import Plugin, ClassDefContext
from mypy.plugins.common import add_method
from mypy.types import CallableType
from mypy.nodes import ARG_POS, Argument, Var

def custom_class_hook(ctx: ClassDefContext) -> None:
    if ctx.cls.name == "MySpecialClass":
        # Add a dummy method to prove it's working
        add_method(
            ctx,
            name="hello_plugin",
            args=[],
            return_type=ctx.api.named_type("builtins.str"),
        )

class MyStubPlugin(Plugin):
    def get_class_decorator_hook(self, fullname):
        return None

    def get_base_class_hook(self, fullname: str):
        # Use this hook to match a base class
        if fullname == "my_package.base.MySpecialBase":
            return custom_class_hook
        return None

def plugin(version: str):
    print("✅ plugin() loaded")
    return MyStubPlugin
