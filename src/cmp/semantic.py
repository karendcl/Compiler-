import itertools as itt
from collections import OrderedDict
from typing import List, Tuple


class SemanticError(Exception):
    @property
    def text(self):
        return self.args[0]

class Attribute:
    def __init__(self, name, typex, value):
        self.name = name
        self.type = typex
        self.value = value

    def __str__(self):
        return f'[attrib] {self.name} : {self.type.name} = {self.value};'

    def __repr__(self):
        return str(self)

class Method:
    def __init__(self, name, param_names, params_types, return_type):
        self.name = name
        self.param_names = param_names
        self.param_types = params_types
        self.return_type = return_type

    def __str__(self):
        if self.param_names != []:
            params = ', '.join(f'{n}:{t.name}' for n,t in zip(self.param_names, self.param_types))
        else:
            params = ''
        return f'[method] {self.name}({params}): {self.return_type.name};'

    def __eq__(self, other):
        return other.name == self.name and \
            other.return_type == self.return_type and \
            other.param_types == self.param_types

class Function:
    def __init__(self, name, param_names, params_types, body):
        self.name = name
        self.param_names = param_names
        self.param_types = params_types
        self.expr = body

    def __str__(self):
        params = ', '.join(f'{n}:{t.name}' for n,t in zip(self.param_names, self.param_types))
        return f'[function] {self.name}({params});'

    def __eq__(self, other):
        return other.name == self.name and \
            other.param_types == self.param_types

class Type:
    def __init__(self, name:str):
        self.name = name
        self.attributes = []
        self.methods = []
        self.parent = None
        self.children = []
        self.orig_parent = None
        self.params = []

    def set_parent(self, parent):
        if self.parent is not None:
            raise SemanticError(f'Parent type is already set for {self.name}.')
        self.parent = parent

        new_methods = parent.methods

        print(self.methods)

        for method in new_methods:
            if method in self.methods:
                raise SemanticError(
                    f'Method {method.name} already defined in {self.name}.')

        self.methods.extend(new_methods)

        for child in self.children:
            for method_ in new_methods:
                child.define_method(method_.name, method_.param_names, method_.param_types, method_.return_type)

        parent.children.append(self)


    def set_params(self, params: List[Tuple]):
        self.params = params

    def get_attribute(self, name:str):
        try:
            return next(attr for attr in self.attributes if attr.name == name)
        except StopIteration:
            raise SemanticError(f'Attribute "{name}" is not defined in {self.name}.')


    def define_attribute(self, name:str, typex, value):
        try:
            self.get_attribute(name)
        except SemanticError:
            attribute = Attribute(name, typex, value)
            self.attributes.append(attribute)
            return attribute
        else:
            raise SemanticError(f'Attribute "{name}" is already defined in {self.name}.')

    def get_method(self, name:str):
        try:
            return next(method for method in self.methods if method.name == name)
        except StopIteration:
            if self.parent is None:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')
            try:
                return self.parent.get_method(name)
            except SemanticError:
                raise SemanticError(f'Method "{name}" is not defined in {self.name}.')

    def define_method(self, name:str, param_names:list, param_types:list, body):
        if name in (method.name for method in self.methods):
            raise SemanticError(f'Method "{name}" already defined in {self.name}')

        method = Function(name, param_names, param_types, body)
        self.methods.append(method)
        for child in self.children:
            child.methods.append(method)
        return method

    def all_attributes(self, clean=True):
        plain = OrderedDict() if self.parent is None else self.parent.all_attributes(False)
        for attr in self.attributes:
            plain[attr.name] = (attr, self)
        return plain.values() if clean else plain

    def all_methods(self, clean=True):
        plain = OrderedDict() if self.parent is None else self.parent.all_methods(False)
        for method in self.methods:
            plain[method.name] = (method, self)
        return plain.values() if clean else plain

    def implements(self, protocol):
        return all(method in self.methods for method in protocol.methods)


    def conforms_to(self, other):
        return (other.bypass() or self == other or
                (self.parent is not None and self.parent.conforms_to(other))
                or self.implements(other))

    def bypass(self):
        return False

    def __str__(self):
        output = f'type {self.name}'
        parent = '' if self.parent is None else f' : {self.parent.name}'
        output += parent
        output += ' {'
        output += '\n\t' if self.attributes or self.methods else ''
        output += '\n\t'.join(str(x) for x in self.attributes)
        output += '\n\t' if self.attributes else ''
        output += '\n\t'.join(str(x) for x in self.methods)
        output += '\n' if self.methods else ''
        output += '}\n'
        return output

    def __repr__(self):
        return str(self)

    @property
    def __hash__(self):
        return hash(self.name)

class Protocol(Type):
    def __init__(self, name:str):
        self.name = name
        self.methods = []
        self.parents = []
        self.children: List[Protocol] = []
        self.orig_parent = []


    def set_parent(self, parent):
        if not isinstance(parent, Protocol):
            raise SemanticError('Protocols can only extend protocols.')

        if parent in self.parents:
            raise SemanticError(f'Protocol {parent.name} already extends {self.name}')

        self.parents.append(parent)
        new_methods = parent.methods
        #if intersection is not null
        for method in self.methods:
            if method in new_methods:
                raise SemanticError(f'Method {method.name} already defined in {self.name} or one of the extending protocols.')

        self.methods.extend(new_methods)

        for child in self.children:
            for method_ in new_methods:
                child.define_method(method_.name, method_.param_names, method_.param_types, method_.return_type)

        parent.children.append(self)


    def get_method(self, name:str):
        try:
            return next(method for method in self.methods if method.name == name)
        except StopIteration:
            raise SemanticError(f'Method "{name}" is not defined in {self.name} or one of the extending protocols.')


    def define_attribute(self, name:str, typex):
        raise SemanticError('Protocols cannot define attributes.')


    def define_method(self, name:str, param_names:list, param_types:list, return_type):
        if name in (method.name for method in self.methods):
            raise SemanticError(f'Method "{name}" already defined in {self.name}')

        method = Method(name, param_names, param_types, return_type)
        self.methods.append(method)
        for child in self.children:
            child.methods.append(method)
        return method

    def __str__(self):
        output = f'protocol {self.name}'
        parent = '' if self.parents == [] else f' : {', '.join(x.name for x in self.parents)}'
        output += parent
        output += ' {'
        output += '\n\t' if self.methods else ''
        output += '\n\t'.join(str(x) for x in self.methods)
        output += '\n' if self.methods else ''
        output += '}\n'
        return output

    def __repr__(self):
        return str(self)
class ObjectType(Type):
    # set property parent
    parent = None
    name = 'object'
    def __init__(self):
        Type.__init__(self, 'object')
        self.parent = None
        self.orig_parent = None

    def __eq__(self, other):
        return other.name == self.name and isinstance(other, ObjectType)

    def __hash__(self):
        return super().__hash__

class ErrorType(Type):
    parent = None
    name = '<error>'
    def __init__(self):
        Type.__init__(self, '<error>')
        self.orig_parent = None

    def conforms_to(self, other):
        return True

    def bypass(self):
        return True

    def __eq__(self, other):
        return isinstance(other, Type)

    def __hash__(self):
        return super().__hash__

class VoidType(Type):
    parent = ObjectType()
    name = 'void'
    def __init__(self):
        Type.__init__(self, '<void>')
        self.orig_parent = ObjectType()

    def conforms_to(self, other):
        raise Exception('Invalid type: void type.')

    def bypass(self):
        return True

    def __eq__(self, other):
        return isinstance(other, VoidType)

    def __hash__(self):
        return super().__hash__

class IntType(Type):
    parent = ObjectType()
    name = 'int'
    def __init__(self):
        Type.__init__(self, 'int')
        self.parent = ObjectType()
        self.orig_parent = ObjectType()

    def __eq__(self, other):
        return other.name == self.name or isinstance(other, IntType)

    def __hash__(self):
        return super().__hash__
class BoolType(Type):
    parent = ObjectType()
    name = 'bool'
    def __init__(self):
        Type.__init__(self, 'bool')
        self.parent = ObjectType()
        self.orig_parent = ObjectType()

    def __eq__(self, other):
        return other.name == self.name and isinstance(other, BoolType)

    def __hash__(self):
        return super().__hash__
class StringType(Type):
    parent = ObjectType()
    name = 'string'
    def __init__(self):
        Type.__init__(self, 'string')
        self.parent = ObjectType()
        self.orig_parent = ObjectType()

    def __eq__(self, other):
        return other.name == self.name and isinstance(other, StringType)

    def __hash__(self):
        return super().__hash__

class NoneType(Type):
    parent = ObjectType()
    name = 'None'
    def __init__(self):
        #Not specified
        Type.__init__(self, 'None')
        self.parent = None
        self.orig_parent = None

    def __hash__(self):
        return super().__hash__

    def conforms_to(self, other):
        return True

    def __eq__(self, other):
        return other.name == self.name and isinstance(other, NoneType)

class IterableType(Type):
    parent = ObjectType()
    name = 'Iterable'
    elem_type = None
    def __init__(self, elem_type = None):
        Type.__init__(self, 'Iterable')
        self.parent = ObjectType()
        self.orig_parent = ObjectType()
        self.elem_type = elem_type

    def __eq__(self, other):
        return other.name == self.name and isinstance(other, IterableType)

    def __hash__(self):
        return super().__hash__


class SelfType(Type):
    parent = ObjectType()
    name = 'Self'
    def __init__(self):
        Type.__init__(self, 'Self')
        self.parent = ObjectType()
        self.orig_parent = ObjectType()

    def __eq__(self, other):
        return other.name == self.name and isinstance(other, SelfType)

    def __hash__(self):
        return super().__hash__

    def __str__(self):
        return 'Self'

    def __repr__(self):
        return str(self)

class Context:
    def __init__(self):
        self.types = {}
        self.protocols = {}

    def create_type(self, name:str):
        if name in self.types:
            raise SemanticError(f'Type with the same name ({name}) already in context.')
        if name in self.protocols:
            raise SemanticError(f'Type with the same name as a protocol ({name}) already in context.')
        typex = self.types[name] = Type(name)
        return typex

    def get_type(self, name:str):
        try:
            return self.types[name]
        except KeyError:
            raise SemanticError(f'Type "{name}" is not defined.')

    def create_protocol(self, name:str):
        if name in self.protocols:
            raise SemanticError(f'Protocol with the same name ({name}) already in context.')
        if name in self.types:
            raise SemanticError(f'Protocol with the same name as a type ({name}) already in context.')
        protocol = self.protocols[name] = Protocol(name)
        return protocol

    def get_protocol(self, name:str):
        try:
            return self.protocols[name]
        except KeyError:
            raise SemanticError(f'Protocol "{name}" is not defined.')

    def get_type_or_protocol(self, name:str):
        if name is None:
            return self.types['None']

        try:
            return self.get_type(name)
        except SemanticError:
            try:
                return self.get_protocol(name)
            except SemanticError:
                raise SemanticError(f'Type or Protocol "{name}" is not defined.')

    def __str__(self):
        a = '{\n\t' + '\n\t'.join(y for x in self.types.values() for y in str(x).split('\n')) + '\n}'
        b = '{\n\t' + '\n\t'.join(y for x in self.protocols.values() for y in str(x).split('\n')) + '\n}'
        return a + '\n' + b

    def __repr__(self):
        return str(self)

class VariableInfo:
    def __init__(self, name, vtype):
        self.name = name
        self.type = vtype

    def __str__(self):
        return f'{self.name} : {self.type.name}'

class FunctionInfo:
    def __init__(self, name, param_names, param_types, expression_body):
        self.name = name
        self.param_names = param_names
        self.param_types = param_types
        self.body = expression_body


    def __str__(self):
        return f'{self.name}({self.param_names})'


class Scope:
    def __init__(self, parent=None):
        self.locals = []
        self.functions = []
        self.parent = parent
        self.children = []
        self.index = 0 if parent is None else len(parent)

    def __len__(self):
        return len(self.locals)

    def create_child(self):
        child = Scope(self)
        self.children.append(child)
        child.functions = self.functions
        return child

    def define_variable(self, vname, vtype):
        info = VariableInfo(vname, vtype)
        self.locals.append(info)
        return info

    def define_function(self,name,param_names, param_types, expression):
        info = FunctionInfo(name, param_names,param_types, expression)
        self.functions.append(info)
        return info

    def find_function(self, name, index = None):
        locals = self.functions
        try:
            return next(x for x in locals if x.name == name and isinstance(x, FunctionInfo))
        except StopIteration:
            return self.parent.find_function(name, self.index) if self.parent is None else None


    def find_variable(self, vname, index=None):
        locals = self.locals if index is None else itt.islice(self.locals, index)
        try:
            return next(x for x in locals if x.name == vname and isinstance(x,VariableInfo))
        except StopIteration:
            return self.parent.find_variable(vname, self.index) if self.parent is None else None

    def is_defined(self, vname):
        return self.find_variable(vname) is not None

    def is_local(self, vname):
        return any(True for x in self.locals if x.name == vname)



    def __str__(self):
        return f'Locals: {','.join(str(x) for x in self.locals)}'

def common_ancestor(t1: Type, t2: Type):
    if t1 == t2:
        return t1
    if isinstance(t1,ObjectType) or isinstance(t2,ObjectType):
        return ObjectType
    if t1 == t2.parent:
        return t2.parent
    if t2 == t1.parent:
        return t1.parent

    return common_ancestor(t1.parent, t2.parent)