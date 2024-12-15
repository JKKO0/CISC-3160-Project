import sys
import string


class InterpreterError(Exception):
    pass


class Token:
    # Represents a token with type and value
    def __init__(self, ttype, value):
        self.ttype = ttype
        self.value = value

    def __repr__(self):
        return f"Token({self.ttype}, {self.value})"


class Lexer:
    # Token types
    IDENTIFIER = 'IDENTIFIER'
    LITERAL = 'LITERAL'
    PLUS = '+'
    MINUS = '-'
    TIMES = '*'
    LPAREN = '('
    RPAREN = ')'
    ASSIGN = '='
    SEMI = ';'
    EOF = 'EOF'

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def error(self, msg):
        raise InterpreterError(f"Lexical error: {msg}")

    def peek(self):
        # Peek at the current character
        if self.pos < self.length:
            return self.text[self.pos]
        return None

    def advance(self):
        # Advance to the next character
        self.pos += 1

    def skip_whitespace(self):
        # Skip whitespace characters
        while self.peek() and self.peek().isspace():
            self.advance()

    def next_token(self):
        # Return the next token from the input
        self.skip_whitespace()
        current_char = self.peek()

        if current_char is None:
            return Token(Lexer.EOF, '')

        # Single-character tokens
        if current_char == '+':
            self.advance()
            return Token(Lexer.PLUS, '+')
        elif current_char == '-':
            self.advance()
            return Token(Lexer.MINUS, '-')
        elif current_char == '*':
            self.advance()
            return Token(Lexer.TIMES, '*')
        elif current_char == '(':
            self.advance()
            return Token(Lexer.LPAREN, '(')
        elif current_char == ')':
            self.advance()
            return Token(Lexer.RPAREN, ')')
        elif current_char == '=':
            self.advance()
            return Token(Lexer.ASSIGN, '=')
        elif current_char == ';':
            self.advance()
            return Token(Lexer.SEMI, ';')

        # Identifiers: start with a letter or underscore, then letters/digits/underscore
        if current_char.isalpha() or current_char == '_':
            start_pos = self.pos
            while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
                self.advance()
            value = self.text[start_pos:self.pos]
            return Token(Lexer.IDENTIFIER, value)

        # Literals: integers only (no leading zeros unless zero itself)
        if current_char.isdigit():
            start_pos = self.pos
            self.advance()
            if self.text[start_pos] != '0':
                while self.peek() and self.peek().isdigit():
                    self.advance()
            else:
                if self.peek() and self.peek().isdigit():
                    self.error("Invalid number format (leading zero).")
            value = self.text[start_pos:self.pos]
            return Token(Lexer.LITERAL, value)

        self.error(f"Unexpected character: {current_char}")

    def tokenize(self):
        # Tokenize the entire input
        tokens = []
        while True:
            token = self.next_token()
            tokens.append(token)
            if token.ttype == self.EOF:
                break
        return tokens


class Parser:
    # Grammar:
    # Program: Assignment*
    # Assignment: Identifier = Exp ;
    # Exp: Exp + Term | Exp - Term | Term
    # Term: Term * Fact | Fact
    # Fact: ( Exp ) | - Fact | + Fact | Literal | Identifier

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def error(self, msg):
        raise InterpreterError(f"Syntax error: {msg}")

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, ttype=None):
        token = self.peek()
        if token is None:
            self.error("Unexpected end of input.")
        if ttype is not None and token.ttype != ttype:
            self.error(f"Expected {ttype}, got {token.ttype}")
        self.pos += 1
        return token

    def parse(self):
        # Parse the entire program
        assignments = []
        while True:
            token = self.peek()
            if token is None or token.ttype == 'EOF':
                break
            assignments.append(self.assignment())
        return assignments

    def assignment(self):
        # Assignment: Identifier = Exp ;
        lhs = self.consume('IDENTIFIER')
        self.consume('=')
        exp = self.exp()
        self.consume(';')
        return ('assign', lhs.value, exp)

    def exp(self):
        # Exp: Exp + Term | Exp - Term | Term
        node = self.term()
        while True:
            token = self.peek()
            if token and token.ttype in ('+', '-'):
                op = self.consume().value
                right = self.term()
                node = (op, node, right)
            else:
                break
        return node

    def term(self):
        # Term: Term * Fact | Fact
        node = self.fact()
        while True:
            token = self.peek()
            if token and token.ttype == '*':
                self.consume('*')
                right = self.fact()
                node = ('*', node, right)
            else:
                break
        return node

    def fact(self):
        # Fact: ( Exp ) | - Fact | + Fact | Literal | Identifier
        token = self.peek()
        if token.ttype == '(':
            self.consume('(')
            node = self.exp()
            self.consume(')')
            return node
        elif token.ttype == '+':
            self.consume('+')
            node = self.fact()
            return ('+', node)
        elif token.ttype == '-':
            self.consume('-')
            node = self.fact()
            return ('-', node)
        elif token.ttype == 'LITERAL':
            val = self.consume('LITERAL').value
            return ('lit', int(val))
        elif token.ttype == 'IDENTIFIER':
            val = self.consume('IDENTIFIER').value
            return ('var', val)
        else:
            self.error("Invalid factor")


class Interpreter:
    def __init__(self, assignments):
        self.assignments = assignments
        self.vars = {}

    def eval_exp(self, node):
        if not isinstance(node, tuple):
            raise InterpreterError("Invalid AST node.")

        nodetype = node[0]

        # Handle literals
        if nodetype == 'lit':
            return node[1]

        # Handle variables
        if nodetype == 'var':
            var_name = node[1]
            if var_name not in self.vars:
                raise InterpreterError(f"Uninitialized variable: {var_name}")
            return self.vars[var_name]

        # Handle unary operators
        # If node has length 2, it's unary
        if nodetype in ('+', '-') and len(node) == 2:
            # Unary plus or minus
            val = self.eval_exp(node[1])
            if nodetype == '+':
                return val  # unary plus just returns the value
            else:
                return -val  # unary minus negates the value

        # Handle binary operators
        # If node has length 3, it's binary
        if nodetype in ('+', '-', '*') and len(node) == 3:
            left = self.eval_exp(node[1])
            right = self.eval_exp(node[2])
            if nodetype == '+':
                return left + right
            elif nodetype == '-':
                return left - right
            elif nodetype == '*':
                return left * right

        raise InterpreterError("Unknown node structure in evaluation.")
    def run(self):
        for assign in self.assignments:
            _, varname, exp = assign
            self.vars[varname] = self.eval_exp(exp)
        for var in sorted(self.vars.keys()):
            print(f"{var} = {self.vars[var]}")


def run_program(program):
    lexer = Lexer(program)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    assignments = parser.parse()
    interpreter = Interpreter(assignments)
    interpreter.run()



if __name__ == "__main__":
    program = """
x = 1;
y = 2;
z = ---(x+y)*(x+-y);
    """
    try:
        run_program(program)
    except InterpreterError as e:
        print(e, file=sys.stderr)
