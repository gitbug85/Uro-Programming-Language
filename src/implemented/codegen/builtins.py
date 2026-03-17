from llvmlite import ir
import llvmlite.binding as llvm

class BuiltInBuilder:
    def __init__(self, module, rttypes):
        self.module = module
        self.rttypes = rttypes

    def emit_print(self):
        int32 = ir.IntType(32)
        void = ir.VoidType()
        int8 = ir.IntType(8)
        int8ptr = int8.as_pointer()

        printf_ty = ir.FunctionType(
            int32,
            [int8ptr],
            var_arg=True
        )
        self.printf = ir.Function(self.module, printf_ty, name="printf")

        fmt_str = "%d\n\0"
        fmt_bytes = bytearray(fmt_str.encode("utf8"))
        fmt_type = ir.ArrayType(int8, len(fmt_bytes))

        global_fmt = ir.GlobalVariable(self.module, fmt_type, name="fstr")
        global_fmt.global_constant = True
        global_fmt.initializer = ir.Constant(fmt_type, fmt_bytes)

        print_ty = ir.FunctionType(void, [int32])
        self.print_int = ir.Function(self.module, print_ty, name="print_int")

        block = self.print_int.append_basic_block(name="entry")
        builder = ir.IRBuilder(block)

        x = self.print_int.args[0]

        fmt_ptr = builder.bitcast(global_fmt, int8ptr)

        builder.call(self.printf, [fmt_ptr, x])
        builder.ret_void()

    def emit_get_and_write(self):
        int8 = ir.IntType(8)
        int32 = ir.IntType(32)
        void = ir.VoidType()

        # declare getchar
        getchar_ty = ir.FunctionType(int32, [])
        self.getchar = ir.Function(self.module, getchar_ty, name="getchar")

        # declare putchar
        putchar_ty = ir.FunctionType(int32, [int32])
        self.putchar = ir.Function(self.module, putchar_ty, name="putchar")

        # ---------- read_byte ----------
        read_ty = ir.FunctionType(int32, [])
        self.read_byte = ir.Function(self.module, read_ty, name="read_byte")

        block = self.read_byte.append_basic_block("entry")
        builder = ir.IRBuilder(block)

        c = builder.call(self.getchar, [])
        byte = builder.trunc(c, int32)

        builder.ret(byte)

        # ---------- write_byte ----------
        write_ty = ir.FunctionType(void, [int32])
        self.write_byte = ir.Function(self.module, write_ty, name="write_byte")

        block = self.write_byte.append_basic_block("entry")
        builder = ir.IRBuilder(block)

        x = self.write_byte.args[0]
        ext = builder.zext(x, int32)

        builder.call(self.putchar, [ext])
        builder.ret_void()

        