from enum import Enum

class SourcePosition:
    def __init__(self, file: str, line: int, column: int, length: int = 1):
        self.file = file
        self.line = line
        self.column = column
        self.length = length

class ErrorType(Enum):
    SYNTAX = "SyntaxError"
    TYPE = "TypeError"
    NAME = "NameError"
    SEMANTIC = "SemanticError"
    INTERNAL = "InternalError"
    CASE = "CaseError"

class Error:
    def __init__(
        self,
        message: str,
        position: SourcePosition,
        error_type: ErrorType,
        related: list[SourcePosition] | None = None
    ):
        self.message = message
        self.position = position
        self.error_type = error_type
        self.related = related or []

class Report:
    def __init__(self, error_manager):
        self.error_manager = error_manager

    def case(self, file: str, line: int, column: int, length: int):
        message = "Wrong case!"
        position = SourcePosition(file, line, column, length)
        error_type = ErrorType.CASE
        error = Error(message, position, error_type)
        self.error_manager.errors.append(error)

class ErrorManager:
    def __init__(self):
        self.errors: list[Error] = []
        self.report = Report(self)

    def has_errors(self) -> bool:
        return any(error.error_type != ErrorType.CASE for error in self.errors)
