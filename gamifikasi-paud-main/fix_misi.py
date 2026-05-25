# Read the file
with open(r"d:\aplikasi semster7\gamifikasi-paud-main\gamifikasi-paud-main\app\routes.py", "r", encoding="utf-8") as f:
    content = f.read()

# Old function text - CORRECT: uses 'Soal' (capital S)
old_func = '''    # Import model soal di dalam fungsi untuk memastikan ketersediaan
    from app.models.question import Soaresult = re.sub(r'from app\.models\.question import (\w+) as _SoalModel', r'from app.models.question import \\1 as _SoalModel', old_func)
    if old_func_v2 in content:
        content = content.replace(old_func_v2, new_func)
        with open(r"d:\aplikasi semster7\gamifikasi-paud-main\gamifikasi-paud-main\app\routes.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("Done - function updated with logging (v2)")
    else:
        print("ERROR: Could not find the function to replace")
        # Debug: show what we're looking for
        print("Looking for text starting with:", repr(old_func[:100]))