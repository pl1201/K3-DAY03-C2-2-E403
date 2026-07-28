import os

root = os.path.dirname(os.path.abspath(__file__))

# Loose files to remove from root because they are safely placed in tests/ or scripts/ or temporary
loose_files = [
    "generate_realistic_data.py",
    "test_logic.py",
    "test_new_tools.py",
    "test_simple.py",
    "TEST_TOOLS.py",
    "clean_explorer.py",
    "move_md_files.py",
    "cleanup.py",
    "cleanup.bat"
]

print("Cleaning up loose root python files...")
deleted = 0
for filename in loose_files:
    filepath = os.path.join(root, filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"  [REMOVED] {filename}")
            deleted += 1
        except Exception as e:
            print(f"  [ERROR] {filename}: {e}")

print(f"\nSuccessfully cleaned {deleted} file(s) from root folder!")
print("Your root directory is now 100% clean and structured!")
