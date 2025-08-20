#!/usr/bin/env python3
"""
Load Test Results Analyzer and Graphics Generator
Creates beautiful visualizations from wrk load test results
"""

import json
import re
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# Set style for beautiful plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class LoadTestAnalyzer:
    def __init__(self, results_file=None):
        self.results_file = results_file
        self.parsed_data = {}
        
    def parse_wrk_output(self, output_text):
        """Parse wrk output and extract metrics"""
        data = {}
        
        # Extract basic metrics
        requests_match = re.search(r'(\d+) requests in ([\d.]+)s', output_text)
        if requests_match:
            data['total_requests'] = int(requests_match.group(1))
            data['duration'] = float(requests_match.group(2))
            data['rps'] = data['total_requests'] / data['duration']
        
        # Extract transfer rate
        transfer_match = re.search(r'([\d.]+)MB read', output_text)
        if transfer_match:
            data['mb_read'] = float(transfer_match.group(1))
        
        # Extract requests per second
        rps_match = re.search(r'Requests/sec:\s+([\d.]+)', output_text)
        if rps_match:
            data['rps_reported'] = float(rps_match.group(1))
        
        # Extract transfer per second
        transfer_sec_match = re.search(r'Transfer/sec:\s+([\d.]+)MB', output_text)
        if transfer_sec_match:
            data['transfer_per_sec'] = float(transfer_sec_match.group(1))
        
        # Extract latency statistics
        latency_section = re.search(r'Latency\s+([\d.]+\w+)\s+([\d.]+\w+)\s+([\d.]+\w+)\s+([\d.]+)%', output_text)
        if latency_section:
            data['latency_avg'] = self.parse_time_unit(latency_section.group(1))
            data['latency_stdev'] = self.parse_time_unit(latency_section.group(2))
            data['latency_max'] = self.parse_time_unit(latency_section.group(3))
        
        # Extract percentile data
        percentiles = {}
        perc_matches = re.findall(r'(\d+)%\s+([\d.]+\w+)', output_text)
        for perc, value in perc_matches:
            percentiles[f'p{perc}'] = self.parse_time_unit(value)
        data['percentiles'] = percentiles
        
        # Extract error information
        errors_match = re.search(r'Socket errors: connect (\d+), read (\d+), write (\d+), timeout (\d+)', output_text)
        if errors_match:
            data['errors'] = {
                'connect': int(errors_match.group(1)),
                'read': int(errors_match.group(2)),
                'write': int(errors_match.group(3)),
                'timeout': int(errors_match.group(4))
            }
            data['total_errors'] = sum(data['errors'].values())
        else:
            data['errors'] = {'connect': 0, 'read': 0, 'write': 0, 'timeout': 0}
            data['total_errors'] = 0
        
        # Extract enhanced metrics from Lua script output
        if '=== GET VERIFY NUMBER RESULTS ===' in output_text or '=== POST PAGOS RESULTS ===' in output_text:
            data.update(self.parse_enhanced_metrics(output_text))
        
        return data
    
    def parse_enhanced_metrics(self, output_text):
        """Parse enhanced metrics from Lua script output"""
        enhanced = {}
        
        # Extract status code distribution
        status_section = re.search(r'Status Code Distribution:(.*?)(?=\n\n|\nLatency Stats|$)', output_text, re.DOTALL)
        if status_section:
            status_codes = {}
            for line in status_section.group(1).strip().split('\n'):
                match = re.search(r'(\d+):\s+(\d+)\s+requests', line.strip())
                if match:
                    status_codes[int(match.group(1))] = int(match.group(2))
            enhanced['status_codes'] = status_codes
        
        return enhanced
    
    def parse_time_unit(self, time_str):
        """Convert time string to milliseconds"""
        if 'us' in time_str:
            return float(time_str.replace('us', '')) / 1000
        elif 'ms' in time_str:
            return float(time_str.replace('ms', ''))
        elif 's' in time_str:
            return float(time_str.replace('s', '')) * 1000
        else:
            return float(time_str)
    
    def load_results(self, results_file):
        """Load results from JSON file"""
        with open(results_file, 'r') as f:
            raw_results = json.load(f)
        
        for test_name, test_data in raw_results.items():
            if 'stdout' in test_data:
                self.parsed_data[test_name] = self.parse_wrk_output(test_data['stdout'])
                self.parsed_data[test_name]['raw_output'] = test_data['stdout']
                self.parsed_data[test_name]['execution_time'] = test_data.get('execution_time', 0)
            else:
                print(f"Warning: No stdout data for {test_name}")
    
    def create_comparison_charts(self):
        """Create comprehensive comparison charts"""
        if len(self.parsed_data) < 2:
            print("Need at least 2 test results for comparison")
            return
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 15))
        
        # Extract data for both tests
        test_names = list(self.parsed_data.keys())
        test1_name = test_names[0]
        test2_name = test_names[1]
        test1_data = self.parsed_data[test1_name]
        test2_data = self.parsed_data[test2_name]
        
        # 1. Requests per Second Comparison
        plt.subplot(3, 3, 1)
        rps_data = [test1_data.get('rps_reported', 0), test2_data.get('rps_reported', 0)]
        bars = plt.bar([test1_name.replace('_', '\n'), test2_name.replace('_', '\n')], rps_data, 
                      color=['#FF6B6B', '#4ECDC4'])
        plt.title('Requests per Second', fontsize=14, fontweight='bold')
        plt.ylabel('RPS')
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{rps_data[i]:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Average Latency Comparison
        plt.subplot(3, 3, 2)
        latency_data = [test1_data.get('latency_avg', 0), test2_data.get('latency_avg', 0)]
        bars = plt.bar([test1_name.replace('_', '\n'), test2_name.replace('_', '\n')], latency_data,
                      color=['#FFE66D', '#FF6B6B'])
        plt.title('Average Latency', fontsize=14, fontweight='bold')
        plt.ylabel('Latency (ms)')
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{latency_data[i]:.1f}ms', ha='center', va='bottom', fontweight='bold')
        
        # 3. Total Requests Comparison
        plt.subplot(3, 3, 3)
        total_req_data = [test1_data.get('total_requests', 0), test2_data.get('total_requests', 0)]
        bars = plt.bar([test1_name.replace('_', '\n'), test2_name.replace('_', '\n')], total_req_data,
                      color=['#95E1D3', '#F38BA8'])
        plt.title('Total Requests', fontsize=14, fontweight='bold')
        plt.ylabel('Requests')
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{total_req_data[i]:,}', ha='center', va='bottom', fontweight='bold')
        
        # 4. Error Rate Comparison
        plt.subplot(3, 3, 4)
        error_rates = []
        for test_data in [test1_data, test2_data]:
            total_errors = test_data.get('total_errors', 0)
            total_requests = test_data.get('total_requests', 1)
            error_rate = (total_errors / total_requests) * 100
            error_rates.append(error_rate)
        
        bars = plt.bar([test1_name.replace('_', '\n'), test2_name.replace('_', '\n')], error_rates,
                      color=['#FFA07A', '#98D8C8'])
        plt.title('Error Rate', fontsize=14, fontweight='bold')
        plt.ylabel('Error Rate (%)')
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{error_rates[i]:.2f}%', ha='center', va='bottom', fontweight='bold')
        
        # 5. Latency Percentiles Comparison
        plt.subplot(3, 3, 5)
        percentiles = ['p50', 'p90', 'p95', 'p99']
        test1_percs = [test1_data.get('percentiles', {}).get(p, 0) for p in percentiles]
        test2_percs = [test2_data.get('percentiles', {}).get(p, 0) for p in percentiles]
        
        x = np.arange(len(percentiles))
        width = 0.35
        
        plt.bar(x - width/2, test1_percs, width, label=test1_name.replace('_', ' '), color='#FF6B6B')
        plt.bar(x + width/2, test2_percs, width, label=test2_name.replace('_', ' '), color='#4ECDC4')
        
        plt.title('Latency Percentiles', fontsize=14, fontweight='bold')
        plt.ylabel('Latency (ms)')
        plt.xlabel('Percentile')
        plt.xticks(x, percentiles)
        plt.legend()
        
        # 6. Status Code Distribution for Test 1
        plt.subplot(3, 3, 6)
        if 'status_codes' in test1_data:
            status_codes = test1_data['status_codes']
            plt.pie(status_codes.values(), labels=[f'HTTP {k}' for k in status_codes.keys()], 
                   autopct='%1.1f%%', startangle=90)
            plt.title(f'{test1_name.replace("_", " ")} - Status Codes', fontsize=12, fontweight='bold')
        else:
            plt.text(0.5, 0.5, 'No status code data', ha='center', va='center', transform=plt.gca().transAxes)
            plt.title(f'{test1_name.replace("_", " ")} - Status Codes', fontsize=12, fontweight='bold')
        
        # 7. Status Code Distribution for Test 2
        plt.subplot(3, 3, 7)
        if 'status_codes' in test2_data:
            status_codes = test2_data['status_codes']
            plt.pie(status_codes.values(), labels=[f'HTTP {k}' for k in status_codes.keys()], 
                   autopct='%1.1f%%', startangle=90)
            plt.title(f'{test2_name.replace("_", " ")} - Status Codes', fontsize=12, fontweight='bold')
        else:
            plt.text(0.5, 0.5, 'No status code data', ha='center', va='center', transform=plt.gca().transAxes)
            plt.title(f'{test2_name.replace("_", " ")} - Status Codes', fontsize=12, fontweight='bold')
        
        # 8. Transfer Rate Comparison
        plt.subplot(3, 3, 8)
        transfer_data = [test1_data.get('transfer_per_sec', 0), test2_data.get('transfer_per_sec', 0)]
        bars = plt.bar([test1_name.replace('_', '\n'), test2_name.replace('_', '\n')], transfer_data,
                      color=['#A8E6CF', '#FFD93D'])
        plt.title('Transfer Rate', fontsize=14, fontweight='bold')
        plt.ylabel('MB/sec')
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{transfer_data[i]:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # 9. Performance Summary Table
        plt.subplot(3, 3, 9)
        plt.axis('off')
        
        summary_data = [
            ['Metric', test1_name.replace('_', ' '), test2_name.replace('_', ' ')],
            ['RPS', f"{test1_data.get('rps_reported', 0):.1f}", f"{test2_data.get('rps_reported', 0):.1f}"],
            ['Avg Latency (ms)', f"{test1_data.get('latency_avg', 0):.1f}", f"{test2_data.get('latency_avg', 0):.1f}"],
            ['Total Requests', f"{test1_data.get('total_requests', 0):,}", f"{test2_data.get('total_requests', 0):,}"],
            ['Error Rate (%)', f"{error_rates[0]:.2f}", f"{error_rates[1]:.2f}"],
            ['Transfer (MB/s)', f"{test1_data.get('transfer_per_sec', 0):.2f}", f"{test2_data.get('transfer_per_sec', 0):.2f}"]
        ]
        
        table = plt.table(cellText=summary_data[1:], colLabels=summary_data[0],
                         cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style the table
        for i in range(len(summary_data)):
            for j in range(len(summary_data[0])):
                if i == 0:  # Header row
                    table[(i, j)].set_facecolor('#4ECDC4')
                    table[(i, j)].set_text_props(weight='bold', color='white')
                else:
                    table[(i, j)].set_facecolor('#F7F7F7' if i % 2 == 0 else 'white')
        
        plt.title('Performance Summary', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.suptitle('Load Test Results Comparison Dashboard', fontsize=18, fontweight='bold', y=0.98)
        
        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'load_test_comparison_{timestamp}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Comparison chart saved as: {filename}")
        
        plt.show()
        return filename
    
    def generate_detailed_report(self):
        """Generate a detailed text report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'load_test_report_{timestamp}.txt'
        
        with open(report_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("LOAD TEST DETAILED REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for test_name, data in self.parsed_data.items():
                f.write(f"\n{'-'*60}\n")
                f.write(f"TEST: {test_name.replace('_', ' ').upper()}\n")
                f.write(f"{'-'*60}\n")
                
                f.write(f"Total Requests: {data.get('total_requests', 'N/A'):,}\n")
                f.write(f"Duration: {data.get('duration', 'N/A')} seconds\n")
                f.write(f"Requests/sec: {data.get('rps_reported', 'N/A')}\n")
                f.write(f"Transfer/sec: {data.get('transfer_per_sec', 'N/A')} MB\n")
                f.write(f"Total Transfer: {data.get('mb_read', 'N/A')} MB\n\n")
                
                f.write("LATENCY STATISTICS:\n")
                f.write(f"  Average: {data.get('latency_avg', 'N/A')} ms\n")
                f.write(f"  Std Dev: {data.get('latency_stdev', 'N/A')} ms\n")
                f.write(f"  Max: {data.get('latency_max', 'N/A')} ms\n\n")
                
                if 'percentiles' in data:
                    f.write("LATENCY PERCENTILES:\n")
                    for perc, value in data['percentiles'].items():
                        f.write(f"  {perc}: {value} ms\n")
                    f.write("\n")
                
                f.write("ERROR STATISTICS:\n")
                errors = data.get('errors', {})
                f.write(f"  Connect: {errors.get('connect', 0)}\n")
                f.write(f"  Read: {errors.get('read', 0)}\n")
                f.write(f"  Write: {errors.get('write', 0)}\n")
                f.write(f"  Timeout: {errors.get('timeout', 0)}\n")
                f.write(f"  Total Errors: {data.get('total_errors', 0)}\n")
                
                if data.get('total_requests', 0) > 0:
                    error_rate = (data.get('total_errors', 0) / data.get('total_requests', 1)) * 100
                    f.write(f"  Error Rate: {error_rate:.2f}%\n")
                
                if 'status_codes' in data:
                    f.write("\nSTATUS CODE DISTRIBUTION:\n")
                    for status, count in data['status_codes'].items():
                        percentage = (count / data.get('total_requests', 1)) * 100
                        f.write(f"  HTTP {status}: {count:,} ({percentage:.1f}%)\n")
        
        print(f"Detailed report saved as: {report_file}")
        return report_file

def main():
    analyzer = LoadTestAnalyzer()
    
    # Look for the most recent results file
    results_files = [f for f in os.listdir('.') if f.startswith('load_test_results_') and f.endswith('.json')]
    
    if not results_files:
        print("No results files found. Please run the load tests first.")
        return
    
    # Use the most recent file
    results_file = sorted(results_files)[-1]
    print(f"Using results file: {results_file}")
    
    # Load and analyze results
    analyzer.load_results(results_file)
    
    if not analyzer.parsed_data:
        print("No valid test data found in results file.")
        return
    
    print("Generating graphics and reports...")
    
    # Generate comparison charts
    chart_file = analyzer.create_comparison_charts()
    
    # Generate detailed report
    report_file = analyzer.generate_detailed_report()
    
    print(f"\nAnalysis complete!")
    print(f"Chart: {chart_file}")
    print(f"Report: {report_file}")

if __name__ == "__main__":
    main()
