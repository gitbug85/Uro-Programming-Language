from rich.console import Console
from rich.text import Text
from tokens import TokTy, Tok
import nodes as Nd
from typing import Any

console = Console()

def print_lexemes(lexemes: list[str]):
    format_strings(lexemes, title="LEXEMES", title_color="bold yellow")

def print_tokens(tokens: list[Tok]):
    names = [token.ty.name for token in tokens] 
    format_strings(names, title="TOKENS", title_color="bold red")

def format_strings(
    strings: list[str],
    title: str = "ERROR",
    title_color: str = "white",
    per_line: int = 6,
) -> None:
    DECORATION_STYLE = "white"
    TITLE_STYLE = title_color
    MAIN_STYLE = "bold black"

    if not strings:
        banner = Text("<<<<<<<<<<<<<<<<<<<<<< ", style=DECORATION_STYLE)
        banner.append(f"{title} (empty)", style=TITLE_STYLE)
        banner.append(" >>>>>>>>>>>>>>>>>>>>>>", style=DECORATION_STYLE)
        console.print(banner)
        return

    banner = Text("<<<<<<<<<<<<<<<<<<<<<< ", style=DECORATION_STYLE)
    banner.append(title, style=TITLE_STYLE)
    banner.append(" >>>>>>>>>>>>>>>>>>>>>>", style=DECORATION_STYLE)
    console.print(banner)

    for i in range(0, len(strings), per_line):
        chunk = strings[i:i + per_line]
        line = Text()
        for j, s in enumerate(chunk):
            if j > 0:
                line.append(", ", style=DECORATION_STYLE)
            line.append(f"{i + j:>3}:{repr(s)}", style=MAIN_STYLE)
        console.print(line)

    footer = Text("<" * len(banner.plain), style=DECORATION_STYLE)
    console.print(footer)