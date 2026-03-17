from pathlib import Path
from llvmlite import binding as llvm
import subprocess
import re
import sys

llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

def encode_path_for_filename(path: Path, root: Path) -> str:
    """
    Convert a source path into a filesystem-safe, unique filename,
    without the original .uro extension.
    """
    rel = path.resolve().with_suffix("")  # Remove .uro
    encoded = "__".join(rel.parts)
    encoded = re.sub(r"[^\w\-.]", "_", encoded)
    return encoded

def write(ir, source_path: Path, cache_root: Path, search_root: Path) -> None:
    """
    Generate an object file and executable from LLVM IR in a cross-platform way.
    Works on Windows, Linux, and macOS.
    """
    cache_root.mkdir(parents=True, exist_ok=True)

    encoded_name = encode_path_for_filename(source_path, search_root)

    # Set file extensions depending on OS
    if sys.platform == "win32":
        obj_path = cache_root / f"{encoded_name}.obj"
        exe_path = cache_root / f"{encoded_name}.exe"
    else:
        obj_path = cache_root / f"{encoded_name}.o"
        exe_path = cache_root / f"{encoded_name}"  # no extension on Linux/macOS

    # Parse LLVM IR
    llvm_module = llvm.parse_assembly(str(ir))
    llvm_module.verify()

    # Create target
    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine(codemodel="small")
    llvm_module.triple = target_machine.triple
    llvm_module.data_layout = str(target_machine.target_data)
    llvm_module.verify()

    # Emit object file
    obj_code = target_machine.emit_object(llvm_module)
    with obj_path.open("wb") as f:
        f.write(obj_code)

    print(f"Object file generated: {obj_path}")

    # Determine compiler and linker flags per platform
    if sys.platform == "win32":
        # Windows: clang-cl
        compiler = "clang-cl"
        compile_args = [
            str(obj_path),
            f"/Fe:{exe_path}",
            "/link",
            "/ENTRY:main",
            "/SUBSYSTEM:CONSOLE",
            # TODO: Optional: let user configure SDK paths
            "ucrt.lib",
            "vcruntime.lib",
            "kernel32.lib",
            "legacy_stdio_definitions.lib",
        ]
    else:
        # Linux/macOS: clang
        compiler = "clang"
        compile_args = [
            str(obj_path),
            "-o",
            str(exe_path),
            "-lm",  # math library if needed
        ]

    # Run compiler/linker
    try:
        result = subprocess.run(
            [compiler, *compile_args],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print("Compiler failed!")
        print("Command:", e.cmd)
        print("Exit code:", e.returncode)
        print("stdout:\n", e.stdout)
        print("stderr:\n", e.stderr)
        raise

    print(f"Executable generated: {exe_path}")