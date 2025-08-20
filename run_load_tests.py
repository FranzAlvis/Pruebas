#!/usr/bin/env python3
"""
Load Testing Orchestrator
Runs wrk commands and captures detailed output for analysis
"""

import subprocess
import time
import json
import re
from datetime import datetime
import os

class LoadTestRunner:
    def __init__(self):
        self.results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def run_wrk_command(self, name, command):
        """Run a wrk command and capture output"""
        print(f"\n{'='*60}")
        print(f"Starting {name} test...")
        print(f"Command: {command}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=400  # 400 seconds timeout (longer than test duration)
            )
            
            end_time = time.time()
            
            self.results[name] = {
                'command': command,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'execution_time': end_time - start_time,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"\n{name} completed in {end_time - start_time:.2f} seconds")
            print(f"Return code: {result.returncode}")
            
            if result.stdout:
                print(f"\nOutput:\n{result.stdout}")
            if result.stderr:
                print(f"\nErrors:\n{result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"ERROR: {name} timed out after 400 seconds")
            self.results[name] = {
                'command': command,
                'error': 'Timeout after 400 seconds',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"ERROR running {name}: {str(e)}")
            self.results[name] = {
                'command': command,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def save_results(self):
        """Save results to JSON file"""
        filename = f"load_test_results_{self.timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {filename}")
        return filename
    
    def run_all_tests(self):
        """Run both load tests"""
        print("Starting Load Testing Suite")
        print(f"Timestamp: {self.timestamp}")
        
        # Test 1: GET verify number
        cmd1 = "wrk -t12 -c3000 -d300s -s get_verify_number_enhanced.lua https://yasta.bancounion.com.bo/gateway/user/verify/number?username=65663503"
        self.run_wrk_command("GET_verify_number", cmd1)
        
        # Wait a bit between tests
        print("\nWaiting 10 seconds before next test...")
        time.sleep(10)
        
        # Test 2: POST pagos
        cmd2 = "wrk -t12 -c3000 -d300s -s post_pagos_enhanced.lua https://ws.pagosbolivia.com.bo:8443/api/pagos/ProcessMessage"
        self.run_wrk_command("POST_pagos", cmd2)
        
        # Save results
        results_file = self.save_results()
        
        print(f"\n{'='*60}")
        print("Load Testing Suite Completed!")
        print(f"Results file: {results_file}")
        print(f"{'='*60}")
        
        return results_file

if __name__ == "__main__":
    runner = LoadTestRunner()
    results_file = runner.run_all_tests()
