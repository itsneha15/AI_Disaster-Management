from detection.heuristic_checker import analyze_pe

result = analyze_pe(r"C:\Windows\System32\notepad.exe")

print(result)