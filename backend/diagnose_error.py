import traceback
import sys
import os

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 Starting Diagnosis...")

try:
    print("📦 Attempting to import app.main...")
    import app.main
    print("✅ Import successful! No syntax or import errors found in app.main.")
except Exception:
    error_msg = traceback.format_exc()
    print("❌ ERROR DETECTED!")
    print(error_msg)
    with open("error_report.txt", "w", encoding="utf-8") as f:
        f.write(error_msg)
    print("\n📝 Error has been saved to 'backend/error_report.txt'")

print("🏁 Diagnosis complete.")
