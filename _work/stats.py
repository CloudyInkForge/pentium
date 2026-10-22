import re
b=open(r"D:\CloudyInkForge\pentium\2611\2611.refactored.html",encoding="utf-8").read()
print("column-count", len(re.findall(r"column-count", b)))
print("class=flow", len(re.findall(r'class="flow"', b)))
print("flow-block divs", len(re.findall(r'<div class="flow-block"', b)))
print("col divs", len(re.findall(r'<div class="col">', b)))
print("NEEDS", len(re.findall(r"NEEDS_HUMAN_REVIEW", b)))
