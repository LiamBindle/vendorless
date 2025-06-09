
# # a stack takes inputs. Some of the inputs might not be resolved yet.


# from ast import Call
# from typing import Any, Callable, Union
# import networkx as nx


# class Parameter:
#     def __init__(self, precursors: list['Parameter'], resolver: Callable):
#         # resolver takes the same number of arguments as precursors, returns resolved value
        
#         # A -> B
#         # A, B -> C

#         # order: A, B, C
#         pass

# class Parameter:
#     def __init__(self, parent: object, attr: str) -> None:
#         self._parent = parent
#         self._parent_attr = attr
#         self._is_resolved = False

#     def set(self, value):
#         self._value = value
#         self._is_resolved = True


# class ServiceBase:
#     def __init__(self, *parameters: list[str]) -> None:
#         for p in parameters:
#             setattr(self, p, Parameter(self, p))
            


# class Service:
#     def __init__(self, name: str, **params: Parameter):
#         self.name = name
#         self.params = params

#     def resolve_params(self):
#         for param in self.params.values():
#             param.resolve(self)

#     def __getattr__(self, name):
#         if name in self.params:
#             return self.params[name].resolve(self)
#         raise AttributeError(f"{name} not found in {self}")

#     def __repr__(self):
#         return f"<Service {self.name}>"

#     def dependencies(self):
#         """Return the set of services this service depends on (via Parameter callables)."""
#         deps = set()
#         for param in self.params.values():
#             if callable(param._value):
#                 code = param._value.__code__
#                 for var in code.co_names:
#                     if var != self.name:
#                         deps.add(var)
#         return deps


# def solve(services: list[Service]):
#     # Build a DAG of service dependencies
#     G = nx.DiGraph()
#     name_map = {s.name: s for s in services}

#     for service in services:
#         G.add_node(service.name)
#         for dep_name in service.dependencies():
#             if dep_name in name_map:
#                 G.add_edge(dep_name, service.name)

#     # Topological sort to resolve in order
#     for name in nx.topological_sort(G):
#         name_map[name].resolve_params()