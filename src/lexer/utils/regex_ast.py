from pydantic import BaseModel


class Node(BaseModel):
    pass

class UnaryNode(Node):
    child: Node

class BinaryNode(Node):
    left: Node
    right: Node

class ClosureNode(UnaryNode):
    pass

class UnionNode(BinaryNode):
    pass

class ConcatNode(BinaryNode):
    pass

class SymbolNode(Node):
    value: str

class AllCharsNode(Node):
    pass

class PlusNode(UnaryNode):
    pass

class InterrogationNode(UnaryNode):
    pass

class ScriptNode(BinaryNode):
    pass