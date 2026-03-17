from pathlib import Path
from lexer import lex
import terminal as term
from codegen.codegen import CodeGenerator
from llvmlite import ir
from write import write
from errors import ErrorManager
from tokens import Tokenizer
from parser import Parser

COMPILER_DIR = Path(__file__).resolve().parent      # .../src/compiler
SRC_DIR = COMPILER_DIR.parent                       # .../src
PROJECT_DIR = SRC_DIR.parent                        # .../PLL V1.0

CACHE_DIR = PROJECT_DIR / "local-cache"             # fixed location
SEARCH_ROOT = PROJECT_DIR.parent                    # dependent location

def compile_file(path: Path) -> None:
    print(f"\n=== Compiling {path} ===")

    with path.open("r", encoding="utf-8") as f:
        file_content = f.read()

    # Front end
    data = lex(file_content)
    term.print_lexemes(data)

    error_manager = ErrorManager()

    tokenizer = Tokenizer(error_manager)
    tokens = tokenizer.tokenize(path.stem, data)
    term.print_tokens(tokens)

    if not error_manager.errors:
        parser = Parser(tokens)
        ast = parser.get_ast(path.stem)

        codegenerator = CodeGenerator(ast, ir.Module(name=path.stem))
        module = codegenerator.generate()
        print(module)
        write(module, path, CACHE_DIR, SEARCH_ROOT)
    else:
        print("Cases are wrong!")

def compile() -> None:
    print(f"Scanning for .uro files under: {SEARCH_ROOT}")

    uro_files = list(SEARCH_ROOT.rglob("*.uro"))

    if not uro_files:
        print("No .uro files found.")
        return

    for uro_files in uro_files:
        compile_file(uro_files)

if __name__ == "__main__":
    compile()
