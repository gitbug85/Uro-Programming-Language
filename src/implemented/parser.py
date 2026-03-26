import nodes as Nd
from tokens import TokTy, Tok

class Parser:
    def __init__(self, tokens: list[Tok]):
        self.tokens = tokens
        self.pos = 0
        self.PRECEDENCE = {
            TokTy.doubequal: 1,
            TokTy.plus: 2,
            TokTy.minus: 2,
            TokTy.times: 3,
            TokTy.divide: 3,
            TokTy.bitwand: 4,
            TokTy.bitwor: 5,
            TokTy.bitwxor: 6,
            TokTy.bitwnot: 7,
            TokTy.lshift: 8,
            TokTy.rshift: 9,
        }

    def get_ast(self, file_name):
        nodes: list[Nd.Node] = []

        while True:
            self.skip_newlines()
            if self.current() is None:
                break
            nodes.append(self.parse_statement())

        return Nd.Object(
            parameters=[],
            body=nodes,
            base=file_name,
            return_type="obj"
        )

    def parse_statement(self) -> Nd.Node:
        keymods = self.parse_keymods()

        tok = self.current()
        if tok.ty == TokTy.ident and self.peek().ty == TokTy.equals:
            return self.parse_assignment(keymods)
        if tok.ty == TokTy.uroif:
            return self.parse_if()
        if tok.ty == TokTy.ident and self.peek().ty != TokTy.lparen:
            return self.parse_macro()

        return self.parse_expression()

    def parse_macro(self) -> Nd.Macro:
        ident = self.expect(TokTy.ident)
        args: list[Nd.Node] = []
        tok = self.current()

        while self.current() and self.current().ty != TokTy.newline:
            args.append(self.parse_expression())
            self.advance()
            if not self.match(TokTy.comma):
                break

        return Nd.Macro(Nd.Identifier(ident.lit), args)

    def parse_if(self) -> Nd.If:
        self.expect(TokTy.uroif)
        self.expect(TokTy.lparen)

        condition = self.parse_expression()

        self.expect(TokTy.rparen)
        self.expect(TokTy.colon)
        body = self.parse_block()
            
        return Nd.If(condition, body)

    def parse_keymods(self):
        """
        1. Can change type? A
        2. Can change subtype? A
        3. Can change literal? A
        4. Carries over keymods into function? D
        5. Immutable forever? A D (Const or init)
        6. Global or local? A D
        7. Access from outside? D
        8. Access from members? D
        9. Sync or async? D
        """
        keymods = [True] * 3
        for _ in range(6):
            keymods.append(False)
        tok = self.current()

        if tok.ty == TokTy.let:
            keymods[0] = False
            keymods[1] = False
            keymods[2] = False
            self.advance()
            return keymods

        order = {
            TokTy.iex: 0,
            TokTy.iflex: 1,
            TokTy.imut: 2
        }

        last = -1

        while True:
            tok = self.current()

            if tok.ty not in order:
                break

            if order[tok.ty] < last:
                self.error("modifier out of order")

            last = order[tok.ty]

            keymods[order[tok.ty]] = False
            self.advance()

        return keymods

    def parse_assignment(self, keymods: list[bool]) -> Nd.Assignment:
        ident = self.expect(TokTy.ident)
        self.expect(TokTy.equals)
        value = self.parse_expression()
        return Nd.Assignment(keymods, ident.lit, value)

    def parse_expression(self, min_prec=0) -> Nd.Node:
        left = self.get_unaries()
        if left == None:
            left = self.parse_postfix()

        while True:
            tok = self.current()
            if tok is None or tok.ty not in self.PRECEDENCE:
                break

            prec = self.PRECEDENCE[tok.ty]
            if prec < min_prec:
                break

            op = tok.ty
            self.advance()

            right = self.parse_expression(prec + 1)

            left = Nd.BinaryOperator(op, left, right)

        return left

    def get_unaries(self):  # May return Nd.UnaryOperator or None
        tok = self.current()
        if tok is None:
            return None

        if tok.ty == TokTy.minus:
            return self.make_unary(tok, TokTy.minus)
        elif tok.ty == TokTy.bitwnot:
             return self.make_unary(tok, TokTy.bitwnot)

        return None

    def make_unary(self, tok, tokty):
        self.advance()
        operand = self.parse_expression(self.PRECEDENCE[tokty] + 1)
        return Nd.UnaryOperator(tok.ty, operand)

    def parse_postfix(self) -> Nd.Node:
        node = self.parse_primary()

        while self.current() is not None:
            tok = self.current()
            if tok.ty == TokTy.dot:
                self.advance()
                member_tok = self.expect(TokTy.ident)
                node = Nd.MemberAccess(node, Nd.Identifier(member_tok.lit))
            elif tok.ty == TokTy.lparen:
                self.advance()
                args = []
                while self.current() and self.current().ty != TokTy.rparen:
                    args.append(self.parse_expression())
                    if not self.match(TokTy.comma):
                        break
                self.expect(TokTy.rparen)
                node = Nd.Call(node, args)
            else:
                break

        return node

    def parse_primary(self) -> Nd.Node:
        tok = self.current()

        if tok is None:
            raise SyntaxError("Unexpected end of input")
        if tok.ty == TokTy.newline:
            raise SyntaxError("Unexpected newline in expression")
        if tok.ty == TokTy.intlit:
            tok = self.advance()
            return Nd.Integer(32, tok.lit)
        if tok.ty == TokTy.boollit:
            tok = self.advance()
            return Nd.Boolean(tok.lit)
        if tok.ty == TokTy.uintlit:
            tok = self.advance()
            return Nd.Unsigned(Nd.Integer(32, tok.lit))
        if tok.ty == TokTy.bytelit:
            tok = self.advance()
            return Nd.Byte(32, tok.lit)
        if tok.ty == TokTy.ident:
            tok = self.advance()
            return Nd.Identifier(tok.lit)
        if tok.ty == TokTy.lparen:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokTy.rparen)
            return expr

        raise SyntaxError(f"Unexpected token: {tok.ty}")
    
    def parse_parameters(self):
        params = []

        self.expect(TokTy.lparen)

        while self.current() and self.current().ty != TokTy.rparen:
            params.append(self.parse_parameter())
            if not self.match(TokTy.comma):
                break
        self.expect(TokTy.rparen)

    def parse_parameter(self):
        keymods = self.parse_keymods()
        ident = self.expect(TokTy.ident)
        if self.current() == TokTy.colon:
            type = self.expect(TokTy.ident).lit
        else:
            type = "undef"

        return Nd.Parameter(Nd.Identifier(ident.lit), Nd.Identifier(type), keymods)
    
    def parse_return_hint(self):
        self.expect(TokTy.doublecolon)

        if self.current() == TokTy.ident:
            type = self.current(TokTy.ident).lit
        else:
            type = "undef" 

        return Nd.Identifier(type)
    
    def parse_block(self):
        self.skip_newlines()
        self.expect(TokTy.indent)
        statements = []

        self.skip_newlines()
        while self.current().ty != TokTy.dedent:
            statements.append(self.parse_statement())
            self.skip_newlines()

        self.expect(TokTy.dedent)
        return statements
        
    def current(self) -> Tok | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self) -> Tok | None:
        tok = self.current()
        self.pos += 1
        return tok

    def expect(self, ty: TokTy) -> Tok:
        tok = self.current()
        if not tok or tok.ty != ty:
            raise SyntaxError(f"Expected {ty}, got {tok.ty if tok else 'None'}")
        self.pos += 1
        return tok

    def peek(self, offset: int = 1) -> Tok:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return Tok.none()

    def match(self, ty: TokTy) -> bool:
        if self.current() and self.current().ty == ty:
            self.pos += 1
            return True
        return False

    def skip_newlines(self):
        while self.current() and self.current().ty == TokTy.newline:
            self.pos += 1
