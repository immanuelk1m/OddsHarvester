#!/usr/bin/env python
"""
Helper script to run last page collection tests with various configurations
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Test file path
TEST_FILE = "tests/test_last_page_collection_2021.py"

def print_header(message):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60)

def run_command(cmd, description):
    """Run a command and display results"""
    print(f"\n📌 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 40)
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        if result.returncode == 0:
            print("✅ Tests completed successfully")
        else:
            print(f"❌ Tests failed with exit code: {result.returncode}")
        return result.returncode
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return 1

def main():
    """Main function to run tests with different configurations"""
    
    print_header("LAST PAGE COLLECTION TEST RUNNER")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if pytest and pytest-xdist are installed
    print("\n🔍 Checking dependencies...")
    check_deps = subprocess.run(
        ["uv", "pip", "list"], 
        capture_output=True, 
        text=True
    )
    
    if "pytest-xdist" not in check_deps.stdout:
        print("Installing pytest-xdist for parallel execution...")
        subprocess.run(["uv", "pip", "install", "pytest-xdist"])
    
    # Test configurations
    test_configs = [
        {
            "name": "Run all tests with 4 parallel workers",
            "cmd": ["uv", "run", "pytest", TEST_FILE, "-n", "4", "-v"]
        },
        {
            "name": "Run with detailed logging (DEBUG level)",
            "cmd": ["uv", "run", "pytest", TEST_FILE, "-n", "4", "-v", "--log-cli-level=DEBUG"]
        },
        {
            "name": "Run single league test (England)",
            "cmd": ["uv", "run", "pytest", 
                   f"{TEST_FILE}::TestLastPageCollection2021::test_last_page_collection[england-england-premier-league-2020-2021]", 
                   "-v", "-s"]
        },
        {
            "name": "Run without parallel execution (sequential)",
            "cmd": ["uv", "run", "pytest", TEST_FILE, "-v", "-s"]
        },
        {
            "name": "Run with minimal output",
            "cmd": ["uv", "run", "pytest", TEST_FILE, "-n", "4", "-q"]
        }
    ]
    
    # Display menu
    print("\n📋 Available test configurations:")
    for i, config in enumerate(test_configs, 1):
        print(f"  {i}. {config['name']}")
    print(f"  {len(test_configs) + 1}. Run all configurations")
    print(f"  0. Exit")
    
    # Get user choice
    try:
        choice = input("\nSelect configuration (0-{}): ".format(len(test_configs) + 1))
        choice = int(choice)
    except (ValueError, KeyboardInterrupt):
        print("\n👋 Exiting...")
        return 0
    
    if choice == 0:
        print("\n👋 Exiting...")
        return 0
    elif choice == len(test_configs) + 1:
        # Run all configurations
        print_header("RUNNING ALL CONFIGURATIONS")
        for config in test_configs:
            run_command(config["cmd"], config["name"])
    elif 1 <= choice <= len(test_configs):
        # Run selected configuration
        config = test_configs[choice - 1]
        print_header(f"RUNNING: {config['name'].upper()}")
        return_code = run_command(config["cmd"], config["name"])
        
        # Show log locations
        if return_code == 0:
            print("\n📁 Output locations:")
            print(f"  • Logs: test_logs/last_page_2021/")
            print(f"  • Results: test_results/")
            print(f"  • Summary: test_logs/last_page_2021/summary_*.log")
    else:
        print("\n❌ Invalid choice")
        return 1
    
    print(f"\n🏁 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return 0

if __name__ == "__main__":
    sys.exit(main())