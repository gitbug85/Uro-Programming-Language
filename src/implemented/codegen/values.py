from llvmlite import ir
import nodes as Nd

class ValueGenerator:
    def __init__(self, ctx, rttypes, rtnames, rttags):
        self.ctx = ctx
        self.rttypes = rttypes
        self.rtnames = rtnames
        self.rttags = rttags
        self.operation_generator = None # Resolved in codegen initialization

    def make_static(self, node: Nd.Node, name: Nd.str, pointers: dict, builder: ir.IRBuilder):
        
        if isinstance(node, Nd.Integer):
            return ir.Constant(self.rttypes.bits_to_int(node.bit), node.value)
        if isinstance(node, Nd.Unsigned):
            inner_node = node.value
            if isinstance(inner_node, Nd.Integer):
                return Nd.Unsigned(ir.Constant(self.rttypes.bits_to_int(inner_node.bit), inner_node.value))
        if isinstance(node, Nd.Boolean):
            return ir.Constant(self.rttypes.i1, node.value)
        if isinstance(node, Nd.BinaryOperator):
            val = self.operation_generator.genbinop(node, builder, pointers)
            return val
        if isinstance(node, Nd.UnaryOperator):
            val = self.operation_generator.genunop(node, builder, pointers)
            return val
        if isinstance(node, Nd.Identifier):
            val = builder.load(pointers[node.value].ptr, name="ldvar")
            return val
        if isinstance(node, Nd.Call):
            if node.identifier == "i":
                if len(arguments) > 1:
                    pass # Error
                if isinstance(arguments[0], Nd.Integer):
                    val = ir.Constant(self.rttypes.bits_to_int(node.bit), node.value)
                    return make_dynamic(val, arguments[0], builder, pointers)
                else:
                    pass # Error
            return

        raise NotImplementedError(f"Cannot generate static value for node: {node.name}")

    def make_dynamic(self, value: ir.Value, node: Nd.Node, builder: ir.IRBuilder, pointers):

        if isinstance(node, Nd.Integer):
            boxed = ir.Constant(self.rttypes.dyni, ir.Undefined)
            payload = ir.Constant(self.rttypes.int, ir.Undefined)

            if node.bit == 8:
                payload = builder.insert_value(payload, value, 0)
                tag = self.rttags.sint8
            elif node.bit == 16:
                payload = builder.insert_value(payload, value, 1)
                tag = self.rttags.sint16
            elif node.bit == 32:
                payload = builder.insert_value(payload, value, 2)
                tag = self.rttags.sint32
            elif node.bit == 64:
                payload = builder.insert_value(payload, value, 3)
                tag = self.rttags.sint64
                
            boxed = builder.insert_value( # Insert tag
                boxed,
                ir.Constant(self.rttypes.i4, tag),
                0 # First index
            )
            boxed = builder.insert_value( # Insert payload
                boxed,
                payload,
                1 # Second index
            )
            return boxed
        if isinstance(node, Nd.BinaryOperator):
            dyn = self.rttypes.dyni

            boxed = ir.Constant(dyn, ir.Undefined)
            payload = ir.Constant(self.rttypes.int, ir.Undefined)
            tag = self.rttags.sint32

            payload = builder.insert_value(payload, value, 2)
            boxed = builder.insert_value( # Insert tag
                boxed,
                ir.Constant(self.rttypes.i4, tag),
                0 # First index
            )
            boxed = builder.insert_value( # Insert payload
                boxed,
                payload,
                1 # Second index
            )
            return boxed
        if isinstance(node, Nd.Identifier):
            payload = ir.Constant(self.rttypes.int, ir.Undefined)
            tag = self.rttags.sint32

            value = pointers[node.value][0]
            payload = builder.insert_value(payload, value, 2)
            boxed = builder.insert_value( # Insert tag
                boxed,
                ir.Constant(self.rttypes.i4, tag),
                0 # First index
            )
            boxed = builder.insert_value( # Insert payload
                boxed,
                payload,
                1 # Second index
            )
            return boxed


        raise NotImplementedError(f"Cannot generate dynamic value for node: {node.name}")
