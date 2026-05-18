"""
durga.py — SuratPro dev runner
Usage: python durga.py
"""
import os
import sys
import subprocess

def clear_pyc():
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.endswith('.pyc'):
                os.remove(os.path.join(root, f))
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git']]

def main():
    print("🔥 SuratPro Dev Runner")
    print("📍 Clearing .pyc cache...")
    clear_pyc()
    print("✅ Cache cleared.")
    print("🚀 Starting Django dev server at http://127.0.0.1:8000/")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python')
    python = venv_python if os.path.exists(venv_python) else sys.executable
    subprocess.run([python, 'manage.py', 'runserver'])

if __name__ == '__main__':
    main()
