Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

appDir = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = appDir

' 0 = ukryte okno; pythonw = GUI bez konsoli
shell.Run "cmd /c uv run pythonw main.py", 0, False
