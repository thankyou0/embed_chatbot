#!/usr/bin/env python3
"""Debug: check what's happening with apostrophe matching inside the container."""

# 1. Read the server-side detection patterns from the actual file
with open('/app/app/services/chat_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the pattern definition
import re
match = re.search(r"_missing_phrases_en = \[(.*?)\]", content, re.DOTALL)
if match:
    block = match.group(1)
    # Find first apostrophe-containing pattern
    for line in block.split("\n"):
        if "don" in line and "have" in line:
            stripped = line.strip().strip(",").strip().strip('"')
            print(f"Pattern: {repr(stripped)}")
            for i, c in enumerate(stripped):
                if not c.isalpha() and c != ' ':
                    print(f"  pos={i} char={repr(c)} ord={ord(c)} hex={hex(ord(c))}")
            break
else:
    print("Pattern block not found!")

# 2. Simulate what happens during response processing
test_response = "I don't have the specific details on tentree's return and exchange policy"
lower = test_response.lower()
print(f"\nResponse: {repr(lower[:80])}")

# Check apostrophe in response
idx = lower.find("don")
if idx >= 0:
    for i in range(idx, min(idx+10, len(lower))):
        c = lower[i]
        print(f"  pos={i} char={repr(c)} ord={ord(c)} hex={hex(ord(c))}")

# 3. Test the match
pattern = "i don't have the"
print(f"\nPattern repr: {repr(pattern)}")
print(f"Match result: {pattern in lower}")

# 4. Now read from the ACTUAL file patterns
lines = content.split('\n')
for i, line in enumerate(lines):
    if '"i don' in line and 'have the"' in line:
        # Extract the string
        s = line.strip().strip(',').strip()
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        print(f"\nActual file pattern: {repr(s)}")
        print(f"Match against response: {s in lower}")
        # Byte-by-byte comparison
        if s not in lower:
            for j, (a, b) in enumerate(zip(s, lower)):
                if a != b:
                    print(f"  First mismatch at pos {j}: pattern={repr(a)}({ord(a)}) vs response={repr(b)}({ord(b)})")
                    break
        break
