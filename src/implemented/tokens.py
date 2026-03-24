from enum import Enum, auto
from dataclasses import dataclass
import cases
from errors import ErrorManager, Error

class TokTy(Enum):
    # Variable operators
    plus = auto()
    minus = auto()
    times = auto()
    divide = auto()
    # Bitwise operations
    bitwand = auto()
    bitwor = auto()
    bitwxor = auto()
    bitwnot = auto()
    lshift = auto()
    rshift = auto()
    # Assignment operators
    equals = auto()
    # Boolean operators
    doubequal = auto()
    # Keymods
    iex = auto()
    iflex = auto()
    imut = auto()
    let = auto()
    var = auto()
    safe = auto()
    ref = auto()
    const = auto()
    init = auto()
    glob = auto()
    loc = auto()
    pub = auto()
    priv = auto()
    prot = auto()
    sync = auto()
    uroasync = auto()
    # Literals
    intlit = auto()
    uintlit = auto()
    boollit = auto()
    bytelit = auto()
    # Seperators & syntax
    lparen = auto()
    rparen = auto()
    dot = auto()
    comma = auto()
    # Control flow
    uroif = auto()
    # Other
    ident = auto()
    indent = auto()
    dedent = auto()
    newline = auto()
    # Idk
    colon = auto()

@dataclass
class Tok:
    ty: TokTy
    lit: object
    ln: int

class Tokenizer:
    def __init__(self, error_manager):
        self.error_manager = error_manager
        self.table = {
            # Variable operators
            "+": TokTy.plus,
            "-": TokTy.minus,
            "*": TokTy.times,
            "/": TokTy.divide,
            # Bitwise operations
            "&": TokTy.bitwand,
            "||": TokTy.bitwor,
            "|": TokTy.bitwxor,
            "!": TokTy.bitwnot,
            "<": TokTy.lshift,
            ">": TokTy.rshift,
            # Assignment operators
            "=": TokTy.equals,
            # Keymods
            "iex": TokTy.iex,
            "iflex": TokTy.iflex,
            "imut": TokTy.imut,
            "let": TokTy.let,
            "var": TokTy.var,
            "safe": TokTy.safe,
            "ref": TokTy.ref,
            "const": TokTy.const,
            "init": TokTy.init,
            "glob": TokTy.glob,
            "loc": TokTy.loc,
            "pub": TokTy.pub,
            "priv": TokTy.priv,
            "prot": TokTy.prot,
            "sync": TokTy.sync,
            "async": TokTy.uroasync,
            # Seperators
            "(": TokTy.lparen,
            ")": TokTy.rparen,
            ".": TokTy.dot,
            ",": TokTy.comma,
            # Control flow
            "if": TokTy.uroif,
            # Other
            "<ind|ent>": TokTy.indent,
            "<ded|ent>": TokTy.dedent,
            "\n": TokTy.newline,
            # Idk
            ":": TokTy.colon,
        }

    def get(self, fl: str, lex: str, ln: int, col: int, leng: int):

        # Integer literal
        if lex.isdigit():
            return Tok(TokTy.intlit, int(lex), ln)

        # Literal using postfix
        if lex[:-1].isdigit():
            if lex[-1:] == "u":
                return Tok(TokTy.uintlit, lex[:-1], ln)
            if lex[-2:] == "by":
                return Tok(TokTy.bytelit, lex[:-2], ln)

        # Operators
        if lex in self.table:
            return Tok(self.table[lex], None, ln)

        # Booleans
        if lex == "true":
            return Tok(TokTy.boollit, 1, ln)
        if lex == "false":
            return Tok(TokTy.boollit, 0, ln)

        # Identifier (default)
        if not cases.is_camel_case(lex) and not cases.is_flat_case(lex):
            self.error_manager.report.case(fl, ln, col, leng)
        return Tok(TokTy.ident, lex, ln)

    def tokenize(self, fl: str, data: list[tuple[str, int, int, int]]):
        tokens: list[Tok] = []

        # Keep consuming until no data left
        while data:
            lex, ln, col, leng = data.pop(0)  # Remove from front
            tok = self.get(fl, lex, ln, col, leng)

            if tok.ty == TokTy.equals:
                if data and data[0][0] == '=':
                    next_lex, next_ln, next_col, next_leng = data.pop(0)
                    tok = Tok(TokTy.doubequal, None, ln)
            if tok.ty == TokTy.bitwxor:
                if data and data[0][0] == '|':
                    next_lex, next_ln, next_col, next_leng = data.pop(0)
                    tok = Tok(TokTy.bitwor, None, ln)

            tokens.append(tok)

        return tokens
