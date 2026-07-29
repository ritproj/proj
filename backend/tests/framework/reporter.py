import json
import os
from typing import List, Dict, Any

class Reporter:
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.results = []
        self.summary = {
            "total": 0,
            "pass": 0,
            "fail": 0,
            "warning": 0,
            "infeasible": 0,
            "slow": 0,
            "timeout": 0,
            "skipped": 0
        }
        self.issues = {"Critical": [], "Major": [], "Minor": []}
        self.benchmarks = []
        self.stabilities = []

    def log_result(self, test_name: str, status: str, details: Dict[str, Any] = None):
        self.summary["total"] += 1
        key = status.lower()
        if "pass with warning" in key:
            self.summary["warning"] += 1
        elif key in self.summary:
            self.summary[key] += 1
        else:
            # Fallback for unexpected status
            if "pass" in key:
                self.summary["pass"] += 1
            elif "fail" in key:
                self.summary["fail"] += 1
                
        res = {
            "test_name": test_name,
            "status": status,
            "details": details or {}
        }
        self.results.append(res)
        
        if status == "FAIL":
            self.issues["Critical"].append(f"Test failed: {test_name} - {details.get('errors', 'Unknown error')}")
        elif status == "WARNING" or status == "PASS WITH WARNING":
            self.issues["Minor"].append(f"Warning in: {test_name} - {details.get('warnings', 'Unknown warning')}")

    def log_benchmark(self, bench_data: Dict[str, Any]):
        self.benchmarks.append(bench_data)

    def log_stability(self, stab_data: Dict[str, Any]):
        self.stabilities.append(stab_data)

    def generate_markdown(self):
        md = [
            "# GreenRoute V5 Test & Benchmark Report",
            "",
            "## Overall Summary",
            f"- **Total Tests Executed:** {self.summary['total']}",
            f"- **Passed:** {self.summary['pass']}",
            f"- **Failed:** {self.summary['fail']}",
            f"- **Infeasible (Safely Rejected):** {self.summary['infeasible']}",
            f"- **Warnings:** {self.summary['warning']}",
            f"- **Slow:** {self.summary['slow']}",
            f"- **Timeouts:** {self.summary['timeout']}",
            f"- **Skipped:** {self.summary['skipped']}",
            ""
        ]
        
        md.append("## Prioritized Issues")
        md.append("### Critical")
        if not self.issues["Critical"]:
            md.append("- None")
        for iss in self.issues["Critical"]:
            md.append(f"- {iss}")
            
        md.append("### Major")
        if not self.issues["Major"]:
            md.append("- None")
        for iss in self.issues["Major"]:
            md.append(f"- {iss}")
            
        md.append("### Minor")
        if not self.issues["Minor"]:
            md.append("- None")
        for iss in self.issues["Minor"]:
            md.append(f"- {iss}")
            
        md.append("")
        
        md.append("## Benchmark Summary")
        if self.benchmarks:
            md.append("| Customers | Solver | Avg Runtime (s) | Avg Distance (km) | Gap % |")
            md.append("|---|---|---|---|---|")
            for b in self.benchmarks:
                md.append(f"| {b['size']} | {b['solver']} | {b.get('avg_runtime', 0):.4f} | {b.get('avg_distance', 0):.2f} | {b.get('gap_pct', 'N/A')} |")
        else:
            md.append("No benchmarks run.")
            
        md.append("")
        md.append("## Stability Summary")
        if self.stabilities:
            for s in self.stabilities:
                md.append(f"### {s['name']}")
                md.append(f"- Distance Var: {s['dist_var']:.4f}")
                md.append(f"- Runtime Var: {s['time_var']:.4f}")
        else:
            md.append("No stability tests run.")
            
        md.append("")
        md.append("## Detailed Results")
        for r in self.results:
            md.append(f"### {r['test_name']}")
            md.append(f"**Status:** {r['status']}")
            if r['details']:
                md.append("```json")
                md.append(json.dumps(r['details'], indent=2))
                md.append("```")
            md.append("")
            
        with open(self.output_file, 'w') as f:
            f.write("\n".join(md))
        print(f"Report saved to {self.output_file}")
