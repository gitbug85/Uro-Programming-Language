#!/usr/bin/env nim
import os, parseopt
import osproc
import std/strformat

# Linux-only: assumes POSIX layout
proc getPythonPath(project: string): string =
  # Virtualenv Python path on Linux
  result = project / "venv" / "bin" / "python"

proc runPythonCompile(allFlag: bool, recursive: bool, files: seq[string]) =
  let exePath = getAppFilename()
  let exeDir = exePath.parentDir()
  let project = exeDir.parentDir().parentDir()
  let compilerPath = project / "src" / "implemented" / "compiler.py"
  
  var args: seq[string] = @[compilerPath, "comp"]

  if allFlag:
    args.add("--all")

  if recursive:
    args.add("--recursive")

  for f in files:
    args.add(f)

  let pythonPath = getPythonPath(project)

  # Force POSIX-style absolute path (Linux-safe)
  let fullPythonPath = pythonPath.expandFilename()

  echo fmt"Using Python path: {fullPythonPath}"

  # Use execProcess assuming Linux shell environment
  let result = execProcess(fullPythonPath, args = args, options = {poStdErrToStdOut})
  echo result

proc cliMain() =
  var
    command = ""
    allFlag = false
    recursive = false
    files: seq[string] = @[]

  if paramCount() < 1:
    quit("No command provided")

  command = paramStr(1)

  if command == "comp":
    var p = initOptParser(commandLineParams()[1..^1])

    for kind, key, val in p.getopt():
      case kind
      of cmdLongOption, cmdShortOption:
        case key
        of "a", "all":
          allFlag = true
        of "r", "recursive":
          recursive = true
        else:
          quit("Unknown option: " & key)
      of cmdArgument:
        files.add(key)
      else:
        discard

    if allFlag or files.len > 0:
      runPythonCompile(allFlag, recursive, files)
    else:
      echo "Nothing to compile."
  else:
    quit("Unknown command: " & command)

when isMainModule:
  cliMain()