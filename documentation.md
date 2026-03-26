# Uro Documentation

## Types

### `int`
- Signed integer type  
- Supports standard arithmetic operations  

### `uint`
- Unsigned integer type  
- Supports standard arithmetic operations 
- Declared by a `u` prefix

### `byte`
- Signed byte type
- Supports signed bitwise operations  
- Declared by a `by` prefix

### `bool`
- Boolean type (`true` / `false`)  
- No direct operations supported  

---

## Macros

Macros provide shorthand for common input/output and casting operations.

| Macro | Description |
|------|-------------|
| `_read <name>` | Reads an integer from `stdin` into `<name>` |
| `_write <name>` | Writes an integer from `<name>` to `stdout` |
| `_int <name>` | Casts `<name>` to an `int` |
| `_byte <name>` | Casts `<name>` to a `byte` |

---

## ⚙️ Operators

### Arithmetic
| Operator | Description |
|----------|-------------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Integer division |

### Bitwise / Shift
| Operator | Description |
|----------|-------------|
| `<` | Shift left |
| `>` | Shift right |
| `&` | Bitwise AND |
| `!` | Bitwise NOT |
| `\|\|` | Bitwise OR |
| `\|` | Bitwise XOR |

### Comparison & Assignment
| Operator | Description |
|----------|-------------|
| `==` | Equality comparison |
| `>=` | Greater than or equal to comparison |
| `<=` | Less than or equal to comparison |
| `>` | Greater than comparison |
| `<` | Less than comparison |
| `=` | Assignment |

---

## Keymods

### `iflex`
- Declares a variable whose subtype cannot be changed
- Recommended for use with built-in operations

> ⚠️ **Note:** Currently, `iflex` should be used when working with built-ins to ensure compatibility.

---

## Miscellaneous

### Built-in Functions

```uro
print(integer)
```

- Outputs an integer value

### Control Flow

```uro
if (condition):
```

- Executes the following block if `condition` evaluates to `true`

---

## Example

```uro
_read num

iflex addition = 4

num = num * num
num = num + addition

iflex isFour = false

if (num == 4):
    isFour = true

if (isFour):
    _write num
```

---

## Notes

- Indentation is significant for control flow blocks.
- `bool` values must be explicitly set (`true` / `false`).
- Use `iflex` when defining constants or values tied to built-in behavior.