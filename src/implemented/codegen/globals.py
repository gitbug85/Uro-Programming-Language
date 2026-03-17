from llvmlite import ir

class GlobalManager:
    def __init__(self, module: ir.Module):
        self.module = module
        self.globals: dict[str, ir.GlobalVariable] = {}

    def create_and_store_global(self, name: str, value: ir.Constant, constant: bool = False) -> ir.GlobalVariable:
        gv = ir.GlobalVariable(self.module, value.type, name=name)
        gv.linkage = "internal"
        gv.global_constant = constant
        gv.initializer = value
        self.globals[name] = gv
        return gv

    def get_global(self, name: str) -> ir.GlobalVariable:
        if name not in self.globals:
            raise NameError(f"Undefined global: {name}")
        return self.globals[name]