from llvmlite import ir

class RTTags():
    def __init__(self):
        self.sint8 = 0
        self.sint16 = 1
        self.sint32 = 2
        self.sint64 = 3
        self.uint8 = 4
        self.uint16 = 5
        self.uint32 = 6
        self.uint64 = 7
        self.flo16 = 8
        self.flo32 = 9
        self.flo64 = 10
        self.char8 = 11
        self.char16 = 12
        self.char32 = 13
        self.char64 = 14

class RTNames:
    def __init__(self):
        self.sintvar = "siv"
        self.uintvar = "uiv"

class RTTypes:
    def __init__(self, module):
        self.ctx = module.context

        self.i1 = ir.IntType(1) # For booleans
        self.i4 = ir.IntType(4) # For tags
        self.i8 = ir.IntType(8)
        self.i16 = ir.IntType(16)
        self.i32 = ir.IntType(32)
        self.i64 = ir.IntType(64)

        self.f16 = ir.HalfType()
        self.f32 = ir.FloatType()
        self.f64 = ir.DoubleType()

        self.c = ir.IntType(8)
        self.c8 = ir.ArrayType(self.c, 1)
        self.c16 = ir.ArrayType(self.c, 2)
        self.c32 = ir.ArrayType(self.c, 3)
        self.c64 = ir.ArrayType(self.c, 4)

        self.int = self.ctx.get_identified_type("int") # For both signed and unsigned integers
        self.int.set_body(
            self.i8,
            self.i16,
            self.i32,
            self.i64
        )

        self.dyni = self.ctx.get_identified_type("dyni")
        self.dyni.set_body(
            self.i4, # Tag
            self.int
        )

        self.flo = self.ctx.get_identified_type("flo")
        self.flo.set_body(
            self.f16,
            self.f32,
            self.f64
        )

        self.dynf = self.ctx.get_identified_type("dynf")
        self.dynf.set_body(
            self.i4, # Tag
            self.flo
        )

    def bits_to_int(self, bits: int):
        if bits == 8:
            return self.i8
        elif bits == 16:
            return self.i16
        elif bits == 32:
            return self.i32
        elif bits == 64:
            return self.i64
        else:
            raise NotImplementedError(f"Cannot generate an integer for bits: {bits}")
