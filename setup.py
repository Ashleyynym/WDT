#!/usr/bin/env python3
"""
Universal setup script for WDT Supply Chain Air Cargo Management System
Works on Windows, macOS, and Linux - Fully automatic!
"""

import os
import sys
import subprocess
import platform
import venv
import shutil

def run_command(command, shell=True, check=True):
    """Run a command and return success status"""
    try:
        print(f"🔄 Running: {command}")
        result = subprocess.run(command, shell=shell, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ Success: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr.strip()}")
        return False

def detect_platform():
    """Detect the current platform"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    else:
        return "linux"

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ is required.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_virtual_environment():
    """Create virtual environment using Python's venv module"""
    print("\n📦 Creating virtual environment...")
    try:
        venv.create("venv", with_pip=True)
        print("✅ Virtual environment created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install dependencies using the appropriate pip command"""
    print("\n📥 Installing dependencies...")
    
    platform_name = detect_platform()
    
    if platform_name == "windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip first
    if not run_command(f"{pip_cmd} install --upgrade pip"):
        print("⚠️  Failed to upgrade pip, continuing anyway...")
    
    # Install requirements
    if run_command(f"{pip_cmd} install -r requirements.txt"):
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("❌ Failed to install dependencies")
        return False

def create_activation_script():
    """Create a simple activation script for the user"""
    platform_name = detect_platform()
    
    if platform_name == "windows":
        script_content = """@echo off
echo Activating WDT Supply Chain virtual environment...
call venv\\Scripts\\activate
echo.
echo Virtual environment activated! You can now run:
echo   python app.py
echo.
echo To deactivate, type: deactivate
cmd /k
"""
        script_file = "activate.bat"
    else:
        script_content = """#!/bin/bash
echo "Activating WDT Supply Chain virtual environment..."
source venv/bin/activate
echo ""
echo "Virtual environment activated! You can now run:"
echo "  python app.py"
echo ""
echo "To deactivate, type: deactivate"
"""
        script_file = "activate.sh"
        # Make the script executable
        os.chmod(script_file, 0o755)
    
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    print(f"✅ Created activation script: {script_file}")

def main():
    """Main setup function"""
    print("🚀 WDT Supply Chain - Universal Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found in current directory")
        return
    
    # Check if virtual environment already exists
    if os.path.exists("venv"):
        print("⚠️  Virtual environment already exists")
        response = input("Do you want to recreate it? (y/N): ").lower()
        if response == 'y':
            print("🗑️  Removing existing virtual environment...")
            shutil.rmtree("venv")
        else:
            print("📝 Using existing virtual environment")
            create_activation_script()
            print("\n🎉 Setup completed!")
            print("\n📋 Next steps:")
            print("🚀 EASIEST - One command to run everything:")
            print("   python run.py")
            print("\n💡 Alternative options:")
            print("1. One-click files:")
            if detect_platform() == "windows":
                print("   Double-click: start.bat")
            else:
                print("   Double-click: start.sh or run: ./start.sh")
            print("2. Manual activation:")
            if detect_platform() == "windows":
                print("   activate.bat")
            else:
                print("   ./activate.sh")
            print("3. Access at: http://localhost:5000")
            return
    
    # Create virtual environment
    if not create_virtual_environment():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Create activation script
    create_activation_script()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("🚀 EASIEST - One command to run everything:")
    print("   python run.py")
    print("\n💡 Alternative options:")
    print("1. One-click files:")
    if detect_platform() == "windows":
        print("   Double-click: start.bat")
    else:
        print("   Double-click: start.sh or run: ./start.sh")
    print("2. Manual activation:")
    if detect_platform() == "windows":
        print("   activate.bat")
    else:
        print("   ./activate.sh")
    print("3. Access at: http://localhost:5000")
    
    print("\n💡 Tip: Use 'python run.py' for the easiest experience - no manual activation needed!")

if __name__ == "__main__":
    main() 