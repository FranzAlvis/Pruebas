#!/usr/bin/env python3
"""
Complete Load Test Suite
Orchestrates the entire load testing process and generates comprehensive reports
"""

import subprocess
import sys
import os
from datetime import datetime

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['matplotlib', 'seaborn', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Installing missing dependencies...")
        for package in missing_packages:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
        print("Dependencies installed successfully!")

def run_load_tests():
    """Run the load testing suite"""
    print("="*80)
    print("COMPLETE LOAD TEST SUITE")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check dependencies
    check_dependencies()
    
    # Run load tests
    print("Step 1: Running load tests...")
    result = subprocess.run([sys.executable, 'run_load_tests.py'], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("ERROR: Load tests failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    print("Load tests completed successfully!")
    print(result.stdout)
    
    # Generate graphics and reports
    print("\nStep 2: Generating graphics and reports...")
    result = subprocess.run([sys.executable, 'generate_graphics.py'], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("ERROR: Graphics generation failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    print("Graphics and reports generated successfully!")
    print(result.stdout)
    
    print("\n" + "="*80)
    print("LOAD TEST SUITE COMPLETED SUCCESSFULLY!")
    print("="*80)
    
    # List generated files
    print("\nGenerated files:")
    files = os.listdir('.')
    for file in sorted(files):
        if (file.startswith('load_test_results_') or 
            file.startswith('load_test_comparison_') or 
            file.startswith('load_test_report_')):
            print(f"  - {file}")
    
    return True

if __name__ == "__main__":
    success = run_load_tests()
    sys.exit(0 if success else 1)
