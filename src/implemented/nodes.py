
class Node:
    def __init__(self, name: str):
        self.name = name

class Module(Node):
    def __init__(self, body: list[Node]):
        super().__init__("MODULE")
        self.body = body

class Assignment(Node):
    def __init__(self, attributes: list[bool], identifier: Identifier, value: Node):
        super().__init__("ASSIGNMENT")
        """
        Attributes:
        1st: Global or local
        2nd: Can change literal
        3nd: Can change subtype
        4th: Reference or owner
        """
        self.attributes = attributes
        self.identifier = identifier
        self.value = value

class Identifier(Node):
    def __init__(self, value: str):
        super().__init__("Identifier")
        self.value = value

class Operatables(Node):
    pass

class Value(Operatables):
    pass

class Integer(Value):
    def __init__(self, bit: int, value: int):
        super().__init__("INTEGER")
        self.bit = bit
        self.value = value

class Unsigned(Value):
    def __init__(self, bit: int, value: int):
        super().__init__("UNSIGNED INTEGER")
        self.bit = bit
        self.value = value

class Float(Value):
    def __init__(self, bit: int, value: float):
        super().__init__("FLOAT")
        self.bit = bit
        self.value = value

class Boolean(Value):
    def __init__(self, value: bool):
        super().__init__("BOOLEAN")
        self.value = value

class Character(Value):
    def __init__(self, value: str):
        super().__init__("CHARACTER")
        self.value = value

class Binary(Value):
    def __init__(self, value: str):
        super().__init__("BINARY")
        self.value = value

class Word(Value):
    def __init__(self, bit: int, value: str):
        super().__init__("WORD")
        self.bit = bit
        self.value = value

class List(Value):
    def __init__(self, value: list[Node], types: list[Identifier]):
        super().__init__("LIST")
        self.value = value
        self.types = types

class NoneValue(Value):
    def __init__(self):
        super().__init__("NONE")

class Object(Value):
    def __init__(
        self,
        parameters: list["Parameter"],
        body: list[Node],
        base: Identifier,
        return_type: Identifier
    ):
        super().__init__("OBJECT")
        self.parameters = parameters
        self.body = body
        self.base = base
        self.return_type = return_type

class Parameter(Node):
    def __init__(self, identifier: Identifier, type: Identifier, keymods: list[bool]):
        super().__init__("PARAMETER")
        self.identifier = identifier
        self.type = type
        self.keymods = keymods

class BinaryOperator(Operatables):
    def __init__(self, op: str, left: Operatables, right: Operatables):
        super().__init__("BINARY OPERATOR")
        self.op = op
        self.left = left
        self.right = right

class UnaryOperator(Operatables):
    def __init__(self, op: str, operand: Operatables):
        super().__init__("UNARY OPERATOR")
        self.op = op
        self.operand = operand

class Pass(Node):
    def __init__(self):
        super().__init__("PASS")

class MemberAccess(Node): # Ex: <var>.<mem>
    def __init__(self, target: Identifier, member: Node):
        super().__init__("MEMBER_ACCESS")
        self.target = target
        self.member = member

class Call(Node): # Ex: <print><()>
    def __init__(
        self,
        identifier: Identifier,
        arguments: list[Node],
    ):
        super().__init__("CALL")
        self.identifier = identifier
        self.arguments = arguments

class Macro(Node):
    def __init__(self, identifier: Identifier, arguments: list[Node]):
        super().__init__("MACRO")
        self.identifier = identifier
        self.arguments = arguments

class If(Node):
    def __init__(self, condition: Node, body: list[Node]):
        self.condition = condition
        self.body = body
        