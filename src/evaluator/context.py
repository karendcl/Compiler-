class Context:
    def __init__(self, Parent = None):
        self.parent = Parent
        self.types = {}
        self.functions = {}
        self.variables = {}    

    def def_type(self, name, value):
        if name not in self.types:
            self.types[name]=value
        else:
            raise Exception(f"Type {name} already defined in this context")

    def def_function(self, name, value):
        if name not in self.functions:
            self.functions[name]=value
        else:
            raise Exception(f"Function {name} already defined in this context")

    def def_variable(self, name, value):
        if name not in self.variables:
            self.variables[name]=value
        else:
            raise Exception(f"Variable {name} already defined in this context")

    def get_type(self, name):
        if name in self.types:
            return self.types[name]
        elif self.parent:
            return self.parent.get_type(name)
        else:
            raise Exception(f"Type {name} does not exist on this context")

    def get_function(self, name, search_parent: bool):
        if name in self.functions:
            return self.functions[name]
        elif self.parent and search_parent:
            return self.parent.get_function(name)
        else:
            raise Exception(f"Function {name} does not exist on this context")

    def get_variable(self, name):
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get_variable(name)
        else:
            raise Exception(f"Variable {name} does not exist on this context")
    
    def edit_var_value(self, name, value):
        if name in self.variables:
            self.variables[name]=value
        elif self.parent:
            self.parent.edit_variable(name,value)
        else:
            raise Exception(f"Variable {name} does not exist on this context")