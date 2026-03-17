import re

# PascalCase (UpperCamelCase) - allow '?'
PASCAL_CASE_PATTERN = re.compile(
    r'^[A-Z][a-z0-9?]*(?:[A-Z][a-z0-9?]*)*$'
)

# camelCase (lowerCamelCase) - allow '?'
CAMEL_CASE_PATTERN = re.compile(
    r'^[a-z][a-z0-9?]*(?:[A-Z][a-z0-9?]*)*$'
)

# flatcase (all lowercase, allow digits, underscores, and '?')
FLAT_CASE_PATTERN = re.compile(
    r'^[a-z0-9?_]+$'
)

def is_pascal_case(s: str) -> bool:
    return bool(PASCAL_CASE_PATTERN.fullmatch(s))

def is_camel_case(s: str) -> bool:
    return bool(CAMEL_CASE_PATTERN.fullmatch(s))

def is_flat_case(s: str) -> bool:
    return bool(FLAT_CASE_PATTERN.fullmatch(s))