from enum import Enum
import nodes as Nd

"""
This class stores data used later on for the code generation and helps keymods in transition from the parser to code generation.
"""

class ScopeRefData:
    def __init__(self, ptr, ty: str, node: Nd.Node):
        self.ptr = ptr
        self.ty = ty
        self.node = node

class AssignRefData(ScopeRefData):
    def __init__(self, ptr, ty: str, node: Nd.Node, signed: bool):
        super().__init__(ptr, ty, node)
        self.attribs = node.keymods
        self.ident = node.identifier
        self.signed = signed

class DefRefData(ScopeRefData):
    def __init__(self, ptr, ty: str, node: Nd.Node):
        super().__init__(ptr, ty, node)
        self.attribs = node.keymods
        self.ident = node.identifier

class AssignAttribs():
    def __init__(self):
        self.iex = False # Cannot change types
        self.iflex = False # Cannot change subtypes
        self.imut = False # Cannot change literal
        self.loc = True # Cannot be accessed outside of this scope without parent

class DefAttribs():
    def __init__(self):
        self.sync = True
        self.chilac = True # Child access: means the thing this definition owns can access it
        self.parac = True #  Parrent access: means the thing that owns this definition can access it
