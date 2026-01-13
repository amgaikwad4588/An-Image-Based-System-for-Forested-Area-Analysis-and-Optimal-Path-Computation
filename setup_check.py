#!/usr/bin/env python3
"""
EcoView Imaging - Setup Validation Script
Checks if all dependencies and requirements are met
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", f"{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_pip():
    """Check if pip is available"""
    try:
        import pip
        print("✅ pip is available")
        return True
    except ImportError:
        print("❌ pip is not available")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'flask',
        'flask_cors', 
        'numpy',
        'PIL',
        'cv2',
        'scipy',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                importlib.import_module('PIL')
            elif package == 'cv2':
                importlib.import_module('cv2')
            elif package == 'flask_cors':
                importlib.import_module('flask_cors')
            else:
                importlib.import_module(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    return missing_packages

def check_files():
    """Check if all required files exist"""
    required_files = [
        'PythonScripts/unified_api.py',
        'treesense/index.html',
        'treesense/tree_species.html',
        'treesense/optimal_path.html',
        'treesense/historical_data.html',
        'treesense/settings.html',
        'treesense/src/assets/css/theme.css',
        'requirements.txt'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ {file_path} is missing")
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} exists")
    
    return missing_files

def install_dependencies():
    """Install missing dependencies"""
    print("\n🔧 Installing missing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    """Main setup validation function"""
    print("🌳 EcoView Imaging - Setup Validation")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python version too old")
        return False
    
    # Check pip
    if not check_pip():
        print("\n❌ Setup failed: pip not available")
        return False
    
    # Check files
    print("\n📁 Checking required files...")
    missing_files = check_files()
    if missing_files:
        print(f"\n❌ Setup failed: {len(missing_files)} files missing")
        return False
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"\n⚠️  {len(missing_packages)} packages missing, attempting to install...")
        if not install_dependencies():
            print("\n❌ Setup failed: Could not install dependencies")
            return False
        
        # Re-check after installation
        print("\n🔄 Re-checking dependencies...")
        missing_packages = check_dependencies()
        if missing_packages:
            print(f"\n❌ Setup failed: Still missing {len(missing_packages)} packages")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup validation completed successfully!")
    print("✅ All requirements met")
    print("✅ Ready to run EcoView Imaging")
    print("\nTo start the application:")
    print("  Windows: Double-click start_ecoview.bat")
    print("  Mac/Linux: ./start_ecoview.sh")
    print("  Manual: python PythonScripts/unified_api.py")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
