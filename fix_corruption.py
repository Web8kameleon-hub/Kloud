p = r"c:\Users\Admin\Desktop\kloud\apps\api\main.py"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

literal_rn = "`r`n"
count = c.count(literal_rn)
print(f"occurrences: {count}")

# Replace all literal backtick-r-n with actual newlines
c = c.replace(literal_rn, "\n")

with open(p, "w", encoding="utf-8") as f:
    f.write(c)
print("Done, wrote file")
