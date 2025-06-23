#!/usr/bin/env python3
"""
One-click launcher for WDT Supply Chain Air Cargo Management System
Automatically activates virtual environment and starts the application
"""

import os
import sys
import subprocess
import platform
import time

def check_virtual_environment():
    """Check if virtual environment exists"""
    return os.path.exists("venv")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def activate_and_run():
    """Activate virtual environment and run the application"""
    platform_name = platform.system().lower()
    
    if platform_name == "windows":
        activate_cmd = "venv\\Scripts\\activate"
        python_cmd = "venv\\Scripts\\python"
    else:
        activate_cmd = "source venv/bin/activate"
        python_cmd = "venv/bin/python"
    
    print("🚀 Starting WDT Supply Chain Air Cargo Management System...")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n📦 Installing missing dependencies...")
        if platform_name == "windows":
            install_cmd = f'cmd /c "{activate_cmd} && {python_cmd} -m pip install -r requirements.txt"'
        else:
            install_cmd = f'bash -c "{activate_cmd} && {python_cmd} -m pip install -r requirements.txt"'
        
        print("🔄 Installing dependencies...")
        result = subprocess.run(install_cmd, shell=True)
        if result.returncode != 0:
            print("❌ Failed to install dependencies")
            return
    
    # Run the application
    try:
        if platform_name == "windows":
            # On Windows, use cmd to run the commands
            cmd = f'cmd /c "{activate_cmd} && {python_cmd} app.py"'
        else:
            # On Unix-like systems, use bash
            cmd = f'bash -c "{activate_cmd} && {python_cmd} app.py"'
        
        print("🔄 Activating virtual environment and starting application...")
        print("📱 The application will be available at: http://localhost:5000")
        print("🌐 Also available at: http://127.0.0.1:5000")
        print("⏹️  Press Ctrl+C to stop the application")
        print("-" * 60)
        
        # Add a small delay to show the message
        time.sleep(1)
        
        subprocess.run(cmd, shell=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("\n💡 Try running the setup again:")
        print("   python setup.py")

def main():
    """Main launcher function"""
    print("🎯 WDT Supply Chain - One-Click Launcher")
    print("=" * 50)
    
    # Check if virtual environment exists
    if not check_virtual_environment():
        print("❌ Virtual environment not found!")
        print("\n📋 Please run the setup first:")
        print("   python setup.py")
        print("\n💡 Or use the universal setup:")
        print("   python setup.py")
        return
    
    # Check if app.py exists
    if not os.path.exists("app.py"):
        print("❌ app.py not found!")
        print("Please make sure you're in the correct directory.")
        return
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        print("Please make sure you're in the correct directory.")
        return
    
    # Start the application
    activate_and_run()

if __name__ == "__main__":
    main() 