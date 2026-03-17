import os, strutils

#[
Summary of this file:
1. Add uro directory to PATH via ~/.profile (if missing)
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

for entry in currentPath.split(':'):
  let trimmed = entry.strip()
  if trimmed.len > 0:
    paths.add(trimmed)

var alreadyPresent = false
for p in paths:
  if p == fullUroDir:
    alreadyPresent = true
    break

if not alreadyPresent:
  let profile = getHomeDir() / ".profile"
  let cmd = "echo '\n# uro\nexport PATH=\"$PATH:" & fullUroDir & "\"' >> \"" & profile & "\""

  runStep(
    "Adding uro directory to user PATH",
    cmd,
    "Unable to modify ~/.profile. This may happen if the file is not writable or your home directory permissions are incorrect."
  )
else:
  echo "[OK] Uro directory already present in PATH."

let venvPath = project / "venv"

var cmd = "python3.14 -m venv \"" & venvPath & "\""
runStep(
  "Creating Python virtual environment",
  cmd,
  "python3.14 was not found. Install Python 3.14 or ensure the 'python3.14' command exists in PATH."
)

let pipExe = venvPath / "bin" / "pip"

if not fileExists(pipExe):
  echo "[ERROR] pip not found in virtual environment."
  echo "[DEFSOL] The Python venv was created incorrectly or Python was built without ensurepip."
  quit("Setup aborted.")

cmd = pipExe & " install llvmlite"
runStep(
  "Installing llvmlite",
  cmd,
  "llvmlite failed to install. This may happen if Python development headers or LLVM dependencies are missing."
)

cmd = pipExe & " install rich"
runStep(
  "Installing rich",
  cmd,
  "pip could not download packages. Check your internet connection or Python package index access."
)

echo ""
echo "Setup complete."
echo "Restart your shell or run:"
echo "    source ~/.profile"
echo "Then you can run:"
echo "    uro comp -a"