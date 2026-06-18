import sys

filepath = r'c:\Users\iyas2\DevSecops Agent\backend\api\router.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('yield json.dumps({"type": "tool_status", "tool": tool_name}) + "\\\\n"', 'yield json.dumps({"type": "tool_status", "tool": tool_name}) + "\\n"')
content = content.replace('yield json.dumps({"type": "message", "content": final_text}) + "\\\\n"', 'yield json.dumps({"type": "message", "content": final_text}) + "\\n"')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement successful")
