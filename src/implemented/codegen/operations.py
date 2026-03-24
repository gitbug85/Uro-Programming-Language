from llvmlite import ir
import nodes as Nd
from tokens import TokTy

class OperationGenerator:
    def __init__(self, value_generator):
        self.value_generator = value_generator

    def genbinop(self, node: Nd.BinaryOperator, builder: ir.IRBuilder, pointers) -> ir.Value:

        def resolve_operand(operand):
            if isinstance(operand, Nd.Identifier):
                var_ptr = pointers[operand.value].ptr

                # Load the value which is either a dynamic type or a integer value
                dyn_struct_or_int = builder.load(var_ptr, name=f"{operand.value}.dynorintval")
                if isinstance(dyn_struct_or_int.type, ir.IntType):
                    return dyn_struct_or_int

                # Extract the payload struct (second element of dyn_struct, index 1)
                payload_struct = builder.extract_value(dyn_struct_or_int, 1, name=f"{operand.value}.payload")

                # Extract the i32 value (third element of payload_struct, index 2)
                val = builder.extract_value(payload_struct, 2, name=f"{operand.value}.val")

                return val
            elif isinstance(operand, Nd.BinaryOperator):
                return self.generate_operation(operand, builder, pointers)
            elif isinstance(operand, Nd.Integer):
                return self.value_generator.make_static(operand, "sistat", pointers, builder)
            elif isinstance(operand, Nd.UnsignedInteger):
                return self.value_generator.make_static(operand, "uistat", pointers, builder)
            elif isinstance(operand, Nd.Byte):
                return self.value_generator.make_static(operand, "sbstat", pointers, builder)

            raise NotImplementedError(f"Unsupported operand type: {type(operand)}")

        left_value = resolve_operand(node.left)
        right_value = resolve_operand(node.right)

        ORDER = { # Rule left type wins means the type on the left is the type that the right one may convert to
            ("si", "ui", "=="): lambda l, r: builder.icmp_signed('==', l, r, "cmp"),
            ("ui", "si", "=="): lambda l, r: builder.icmp_unsigned('==', l, r, "cmp")
            
        }

        if left_value.type != right_value.type:
            raise TypeError("Type mismatch in binary operation" + left_value.type.intrinsic_name + right_value.type.intrinsic_name)
            
        if node.op == TokTy.plus:
            return builder.add(left_value, right_value, "result") # Ag
        elif node.op == TokTy.minus:
            return builder.sub(left_value, right_value, "result") # Ag
        elif node.op == TokTy.times:
            return builder.mul(left_value, right_value, "result") # Ag
        elif node.op == TokTy.divide:
            return builder.sdiv(left_value, right_value, "result") # Sn
        elif node.op == TokTy.doubequal:
            return builder.icmp_signed('==', left_value, right_value, "cmp") # Sn
        elif node.op == TokTy.bitwand:
            return builder.and_(left_value, right_value, "result") # Ag
        elif node.op == TokTy.bitwor:
            return builder.or_(left_value, right_value, "result") # Ag
        elif node.op == TokTy.bitwxor:
            return builder.xor(left_value, right_value, "result") # Ag
        elif node.op == TokTy.bitwnot:
            return builder.not_(left_value, "result") # Ag
        elif node.op == TokTy.lshift:
            return builder.shl(left_value, right_value, "result") # Ag
        elif node.op == TokTy.rshift:
            return builder.ashr(left_value, right_value, "result") # Sn

        raise NotImplementedError(f"Unsupported operator: {node.op}")

    def genunop(self, node: Node.UnaryOperator, builder: ir.IRBuilder, pointers):
        op = node.op
        operand = node.operand
        if op == TokTy.minus:
            if isinstance(operand, Nd.Identifier):
                val = builder.load(pointers[operand.value][0], name="ldvar")
                newval = builder.neg(val, name="negi")
                return newval
            if isinstance(operand, Nd.Integer):
                operand.value = -operand.value
                return self.value_generator.make_static(operand, "istat", pointers, builder)
        if op == TokTy.bitwnot:
            if isinstance(operand, Nd.Identifier):
                val = builder.load(pointers[operand.value][0], name="ldvar")
                newval = builder.not_(val, name="notw")
                return newval
            if isinstance(operand, Nd.Byte):
                val = self.value_generator.make_static(operand, "bstat", pointers, builder)
                newval = builder.not_(val, name="notw")
                return newval

        raise NotImplementedError(f"Unsupported operator: {node.op}")
            