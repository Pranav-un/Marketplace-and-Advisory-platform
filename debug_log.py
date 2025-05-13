"""
This script can be imported at the top of settings.py temporarily to help debug issues.
"""
import sys
import os

def log_environment():
    """Log environment variables and system information"""
    with open('debug_info.txt', 'w') as f:
        f.write("Python version: {}\n".format(sys.version))
        f.write("Python path: {}\n".format(sys.path))
        f.write("\nEnvironment Variables:\n")
        for key, value in os.environ.items():
            # Skip sensitive variables
            if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'password', 'token']):
                f.write("{}: [REDACTED]\n".format(key))
            else:
                f.write("{}: {}\n".format(key, value))
        
        f.write("\nDirectory Contents:\n")
        for root, dirs, files in os.walk('.', topdown=True, maxdepth=2):
            f.write("Directory: {}\n".format(root))
            for name in files:
                f.write("  File: {}\n".format(name))
            for name in dirs:
                f.write("  Dir: {}\n".format(name))

# Call immediately when imported
log_environment() 