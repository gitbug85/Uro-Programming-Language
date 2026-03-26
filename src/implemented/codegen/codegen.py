from llvmlite import ir
import llvmlite.binding as llvm

import nodes as Nd

from .rtspecific import RTTypes, RTNames, RTTags
from .values import ValueGenerator
from .globals import GlobalManager
from .operations import OperationGenerator
from .builtins import BuiltInBuilder
from .scope_data import AssignRefData

class CodeGenerator:
    def __init__(self, ast: Nd.Module, module: ir.Module):
        self.ast = ast
        self.module = module

        self.main_builder = None
        self.main_pointers = {} # Basically scope

        triple = llvm.get_process_triple()
        self.module.triple = triple
        target = llvm.Target.from_triple(triple)
        machine = target.create_target_machine()
        self.module.data_layout = str(machine.target_data)
        self.target_data = machine.target_data

        self.rttypes = RTTypes(module)
        self.rtnames = RTNames()
        self.rttags = RTTags()
        self.value_generator = ValueGenerator(self.module.context, self.rttypes, self.rtnames, self.rttags)
        self.global_manager = GlobalManager(module)
        self.operation_generator = OperationGenerator(self.value_generator)
        self.value_generator.operation_generator = self.operation_generator
        self.built_in_builder = BuiltInBuilder(self.module, self.rttypes)

    def generate(self):
        self.emit_main()
        self.emit_builtins()
        self.emit_nodes(self.ast.body)
        self.main_builder.ret(ir.IntType(32)(0)) # End to main
        return self.module

    def emit_main(self):
        main_fn_ty = ir.FunctionType(ir.IntType(32), []) # <- Update return type later
        self.main_fn = ir.Function(self.module, main_fn_ty, name="main")

        block = self.main_fn.append_basic_block(name="entry")

        self.main_builder = ir.IRBuilder(block)

    def emit_builtins(self): # Includes temperary code built by chatgpt
        self.built_in_builder.emit_print()
        self.built_in_builder.emit_get_and_write()

    def emit_nodes(self, nodes):

        for node in nodes:
            if isinstance(node, Nd.Assignment):
                self.generate_assignment(node)
            if isinstance(node, Nd.Call):
                # Check if built-in first
                if node.identifier.value == "print": # Integers for now
                    if isinstance(node.arguments[0], Nd.Identifier):
                        ident_node = node.arguments[0]
                        name = node.identifier.value
                        val = self.get_static_value(ident_node, name)
                    else:
                        int_node = node.arguments[0]
                        ident_node = node.identifier
                        val = self.get_static_value(int_node, ident_node)
                    self.main_builder.call(self.built_in_builder.print_int, [val])
                
            if isinstance(node, Nd.If):
                cond = self.value_generator.make_static(node.condition, "cond", self.main_pointers, self.main_builder)

                then_branch = self.main_builder.append_basic_block("then")
                merge_branch = self.main_builder.append_basic_block("ifcont")

                self.main_builder.cbranch(cond, then_branch, merge_branch)

                self.main_builder.position_at_start(then_branch)
                self.emit_nodes(node.body)
                self.main_builder.branch(merge_branch)  # Jump to merge

                # Merge block
                self.main_builder.position_at_start(merge_branch)
            if isinstance(node, Nd.Macro):
                if node.identifier.value == "_byte":
                    if len(node.arguments) == 1:
                        self.main_pointers[node.arguments[0].value][1] = Nd.Byte("0", "0").name
                if node.identifier.value == "_int":
                    if len(node.arguments) == 1:
                        self.main_pointers[node.arguments[0].value][1] = Nd.Integer(32, 0).name
                if node.identifier.value == "_read":
                    if len(node.arguments) == 1:
                        val = self.main_builder.call(self.built_in_builder.read_byte, [])
                        ptr = self.main_builder.alloca(val.type, name=node.identifier.value)

                        # Store the value
                        self.main_builder.store(val, ptr)

                        # Track the data for future reference
                        self.main_pointers[node.arguments[0].value] = AssignRefData(ptr, node.identifier.value, Nd.Assignment([False] * 9, Nd.Identifier(node.identifier.value), Nd.Pass()))
                if node.identifier.value == "_write":
                    if len(node.arguments) == 1:
                        identifier = node.arguments[0].value
                        val = self.main_builder.load(self.main_pointers[identifier].ptr, "write")
                        byte = self.main_builder.trunc(val, self.rttypes.i32)
                        self.main_builder.call(self.built_in_builder.write_byte, [byte])

    def generate_assignment(self, node: Nd.Assignment):
        initializer_node = node.value
        ident_node = node.identifier
        value = self.get_static_value(initializer_node, ident_node)
        signed = True

        if isinstance(value, Nd.Unsigned):
            value = value.value
            signed = False

        if value is None:
            return

        if node.identifier in self.main_pointers:
            sco_data = self.main_pointers[node.identifier]
            ptr = sco_data.ptr # First element being the pointer
            origin_node = sco_data.node
            origin_keymods = origin_node.keymods

            if origin_keymods[1]:
                value = self.value_generator.make_dynamic(value, origin_node.value, self.main_builder, self.main_pointers)

            # Store the value
            self.main_builder.store(value, ptr)
        else: # The variable has not been assigned before
            if node.keymods[1]:
                value = self.value_generator.make_dynamic(value, initializer_node, self.main_builder, self.main_pointers)

            # Global assignment
            if node.keymods[5]:
                self.global_manager.create_and_store_global(ident_node, value)
                return

            ptr = self.main_builder.alloca(value.type, name=ident_node)

            # Store the value
            self.main_builder.store(value, ptr)

            # Track the data for future reference
            self.main_pointers[ident_node] = AssignRefData(ptr, initializer_node.name, node, signed) # Initializer name is stored for use in signed vs unsigned integers

    def get_static_value(self, node, name):
        return self.value_generator.make_static(
            node,
            name,
            self.main_pointers,
            self.main_builder
        )
