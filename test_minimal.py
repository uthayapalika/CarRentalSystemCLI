# test_minimal.py
print("Hello from test_minimal.py!")

try:
    import sys
    print(f"Python version: {sys.version}")
    
    from db_setup import Database
    print("✅ Database imported")
    
    from factories import ModelFactory
    print("✅ ModelFactory imported")
    
    from version import APP_VERSION
    print(f"✅ Version: {APP_VERSION}")
    
    from views.login_view_cli import LoginViewCLI
    print("✅ LoginViewCLI imported")
    
    print("All imports successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("Test complete!")