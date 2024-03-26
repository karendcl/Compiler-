from itertools import islice
from typing import Union

from src.semantic_checker.toold.types import Variable, Constant, Function, Type, Protocol


class Scope:
    def __init__(self, parent=None):
        self.local_vars: list[Variable] = []
        self.local_funcs: list[Function] = []
        self.parent = parent
        self.children = []
        self.index = 0 if parent is None else len(parent)

    def __len__(self):
        return len(self.local_vars)

    def create_child(self):
        child = Scope(self)
        self.children.append(child)
        return child

    def define_variable(self, name: str, type: Union[Type, Protocol, None] = None):
        info = Variable(name, type)
        self.local_vars.append(info)
        return info

    def define_constant(self, name: str, type: Union[Type, Protocol]):
        info = Constant(name, type)
        self.local_vars.append(info)
        return info

    def define_function(
        self,
        name: str,
        params: list[tuple[str, Union[Type, Protocol, None]]],
        type: Union[Type, Protocol, None] = None,
    ):
        info = Function(name, params, type)
        self.local_funcs.append(info)
        return info

    def find_variable(self, name: str, index=None):
        locals = self.local_vars if index is None else islice(self.local_vars, index)

        try:
            return next(x for x in locals if x.name == name)
        except StopIteration:
            return (
                self.parent.find_variable(name, self.index)
                if self.parent is not None
                else None
            )

    def find_function(self, name: str, index=None):
        local_funcs = self.local_funcs if index is None else islice(self.local_funcs, index)
        try:
            return next(x for x in local_funcs if x.name == name)
        except StopIteration:
            return (
                self.parent.find_function(name, self.index)
                if self.parent is not None
                else None
            )

    def is_defined(self, name: str):
        return self.find_variable(name) is not None

    def is_local(self, name: str):
        return any(True for x in self.local_vars if x.name == name)