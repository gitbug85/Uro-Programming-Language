def lex(file_content: str):
    separators = {
        '.', '(', ')', '[', ']', '{', '}', ',', ':',
        ">", "<", "+", "-", "*", "/", "%", "!", "$",
        "&", "|", "@", "=", ";"
    }

    lexemes: list[tuple[str, int, int, int]] = []
    buffer = ""

    in_horizontal_comment = False
    in_vertical_comment = False
    in_string = False
    in_char = False

    indent_stack: list[int] = [0]
    at_line_start = True
    current_leading = 0

    line = 1
    column = 1
    token_line = 1
    token_column = 1

    i = 0
    length = len(file_content)

    def emit(token: str, token_line: int, token_column: int):
        lexemes.append((token, token_line, token_column, len(token)))

    def handle_indent():
        nonlocal current_leading, at_line_start
        new_indent = current_leading

        if new_indent > indent_stack[-1]:
            indent_stack.append(new_indent)
            emit("<ind|ent>", line, 1)
        else:
            while len(indent_stack) > 1 and indent_stack[-1] > new_indent:
                indent_stack.pop()
                emit("<ded|ent>", line, 1)
            if indent_stack[-1] != new_indent:
                raise ValueError("Inconsistent indentation")

        at_line_start = False
        current_leading = 0

    while i < length:
        char = file_content[i]

        # Horizontal comment
        if in_horizontal_comment:
            if char == '\n':
                in_horizontal_comment = False
            else:
                i += 1
                column += 1
                continue

        # Vertical comment
        if in_vertical_comment:
            if char == '#' and i + 1 < length and file_content[i + 1] == '#':
                in_vertical_comment = False
                i += 2
                column += 2
                continue
            else:
                i += 1
                column += 1
                continue

        # String literal
        if in_string:
            buffer += char
            if char == '"':
                emit(buffer, token_line, token_column)
                buffer = ""
                in_string = False
            i += 1
            column += 1
            continue

        # Char literal
        if in_char:
            buffer += char
            if char == "'":
                emit(buffer, token_line, token_column)
                buffer = ""
                in_char = False
            i += 1
            column += 1
            continue

        # Vertical comment start
        if char == '#' and i + 1 < length and file_content[i + 1] == '#':
            if buffer:
                emit(buffer, token_line, token_column)
                buffer = ""
            in_vertical_comment = True
            i += 2
            column += 2
            continue

        # Horizontal comment start
        if char == '#':
            if buffer:
                emit(buffer, token_line, token_column)
                buffer = ""
            in_horizontal_comment = True
            i += 1
            column += 1
            continue

        # String start
        if char == '"':
            if buffer:
                emit(buffer, token_line, token_column)
                buffer = ""
            if at_line_start:
                handle_indent()
            buffer = '"'
            token_line = line
            token_column = column
            in_string = True
            i += 1
            column += 1
            continue

        # Char start
        if char == "'":
            if buffer:
                emit(buffer, token_line, token_column)
                buffer = ""
            if at_line_start:
                handle_indent()
            buffer = "'"
            token_line = line
            token_column = column
            in_char = True
            i += 1
            column += 1
            continue

        # Separators
        if char in separators:
            if buffer:
                emit(buffer, token_line, token_column)
                buffer = ""
            if at_line_start:
                handle_indent()
            emit(char, line, column)
            i += 1
            column += 1
            continue

        # Newline
        if char == '\n':
            if buffer:
                emit(buffer, token_line, token_column)
                buffer = ""
            emit("\n", line, column)
            at_line_start = True
            current_leading = 0
            line += 1
            column = 1
            i += 1
            continue

        # Whitespace
        if char in {' ', '\t'}:
            if at_line_start:
                if char == ' ':
                    current_leading += 1
                else:
                    current_leading += 8 - (current_leading % 8)
            else:
                if buffer:
                    emit(buffer, token_line, token_column)
                    buffer = ""
            i += 1
            column += 1
            continue

        # Regular character
        if at_line_start:
            handle_indent()
        if not buffer:
            token_line = line
            token_column = column
        buffer += char
        i += 1
        column += 1

    # Flush buffer at EOF
    if buffer:
        emit(buffer, token_line, token_column)

    # Close indents
    while len(indent_stack) > 1:
        indent_stack.pop()
        emit("<ded|ent>", line, 1)

    return lexemes