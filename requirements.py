import subprocess
import sys
import os

def install_requirements():
    """Install all required packages for GitSwift"""
    requirements = [
        'gitpython',
        'PyGithub',
        'pywin32;platform_system=="Windows"'
    ]

    print("Installing required packages...")
    
    for package in requirements:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            return False
    
    print("\nAll requirements installed successfully!")
    print("\nYou can now run GitSwift by executing: python GitSwift.py")
    return True

if __name__ == "__main__":
    install_requirements()