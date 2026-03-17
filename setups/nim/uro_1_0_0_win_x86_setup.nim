import os, strutils

#[
Summary of this file:
1. Add uro directory and executable to user PATH (only if not already present)
2. Create the Python venv
3. Install llvmlite and rich
]#

proc runStep(step: string, command: string, definiteProblem: string = "") =
  echo "[*] " & step
  echo "    " & command
  let code = execShellCmd(command)

  if code != 0:
    echo "[ERROR] Command failed with code " & $code
    if definiteProblem.len > 0:
      echo "[DEFSOL] " & definiteProblem
    quit("Setup aborted.")
  else:
    echo "[OK] " & step

let current = getCurrentDir()
let project = current.parentDir().parentDir()

let uroDir = project / "bin" / "compiled"
let fullUroDir = uroDir.absolutePath().normalizedPath()

let currentPath = getEnv("PATH")
var paths: seq[string] = @[]

for entry in currentPath.split(';'):
  let trimmed = entry.strip()
  if trimmed.len > 0:
    paths.add(trimmed)

let targetPathLower = fullUroDir.toLowerAscii()

var alreadyPresent = false
for p in paths:
  if p.toLowerAscii() == targetPathLower:
    alreadyPresent = true
    break

if not alreadyPresent:
  paths.add(fullUroDir)
  let newPath = paths.join(";")

  let cmd = "reg add HKCU\\Environment /v PATH /t REG_EXPAND_SZ /d \"" & newPath & "\" /f"

  runStep(
    "Adding uro directory to user PATH",
    cmd,
    "Failed to modify the Windows PATH registry entry. This can happen if the registry is locked or the user account does not have permission to modify HKCU\\Environment."
  )
else:
  echo "[OK] Uro directory already present in PATH."

let venvPath = project / "venv"

var cmd = "python3.14 -m venv \"" & venvPath & "\""
runStep(
  "Creating Python virtual environment",
  cmd,
  "python3.14 was not found. Install Python 3.14 and ensure it is added to PATH (enable 'Add Python to PATH' during installation)."
)

let pipExe = venvPath / "Scripts" / "pip.exe"

if not fileExists(pipExe):
  echo "[ERROR] pip.exe not found in virtual environment."
  echo "[DEFSOL] The Python virtual environment was created incorrectly or Python was installed without the ensurepip module."
  quit("Setup aborted.")

cmd = pipExe & " install llvmlite"
runStep(
  "Installing llvmlite",
  cmd,
  "llvmlite failed to install. This may happen if Python development components or required build dependencies are missing."
)

cmd = pipExe & " install rich"
runStep(
  "Installing rich",
  cmd,
  "pip failed to download packages. This is usually caused by no internet connection or blocked access to PyPI."
)

echo ""
echo "Setup complete."
echo "Please restart your computer for PATH changes to take effect."
echo "Afterwards you may need to open the venv/Scripts folder."
echo "Then you can run:"
echo "    uro comp -a"