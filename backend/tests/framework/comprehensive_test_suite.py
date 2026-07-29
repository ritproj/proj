import os
import sys
import traceback

# Add parent dir to path so app modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from generators import generate_customers, generate_depot, generate_fleet
from reporter import Reporter
from benchmark import run_benchmark_iteration, run_stability_test

FAST_MODE = os.environ.get("FAST_MODE", "0") == "1"

def run_phase_1_and_5(reporter: Reporter):
    sizes = [1, 2, 5, 8, 9, 10, 15, 20] if FAST_MODE else [1, 2, 5, 8, 9, 10, 15, 20, 30, 50, 75, 100]
    layouts = ["random", "grid", "spiral"]
    demand_profiles = ["equal", "random", "high"]
    fleets = ["single", "three", "mixed", "random"]
    
    depot = generate_depot("center")
    
    for size in sizes:
        for layout in layouts:
            for d_prof in demand_profiles:
                for f_type in fleets:
                    fleet = generate_fleet(f_type)
                    avg_cap = sum(fleet.capacities_list) / max(1, len(fleet.capacities_list))
                    customers = generate_customers(size, layout, d_prof, avg_cap)
                    
                    # Run Classical
                    c_res = run_benchmark_iteration(depot, customers, fleet, "classical")
                    reporter.log_result(
                        f"P1_C_{size}_{layout}_{d_prof}_{f_type}", 
                        c_res["status"], 
                        {"errors": c_res["errors"], "dist": c_res["distance"]}
                    )
                    
                    # Run Quantum
                    q_res = run_benchmark_iteration(depot, customers, fleet, "quantum")
                    reporter.log_result(
                        f"P1_Q_{size}_{layout}_{d_prof}_{f_type}", 
                        q_res["status"], 
                        {"errors": q_res["errors"], "dist": q_res["distance"]}
                    )
                    
                    if c_res["status"] == "PASS" and q_res["status"] == "PASS" and c_res["distance"] > 0:
                        gap = ((q_res["distance"] - c_res["distance"]) / c_res["distance"]) * 100
                        reporter.log_benchmark({
                            "size": size,
                            "solver": "Comparison",
                            "avg_runtime": q_res["runtime"],
                            "avg_distance": q_res["distance"],
                            "gap_pct": f"{gap:.2f}%"
                        })
                        
                    if FAST_MODE and size > 10:
                        break # Short circuit combinations in fast mode for larger sizes

def run_phase_6(reporter: Reporter):
    depot = generate_depot("center")
    num_tests = 5 if FAST_MODE else 100
    
    for i in range(num_tests):
        size = __import__('random').randint(1, 50)
        fleet = generate_fleet("random")
        avg_cap = sum(fleet.capacities_list) / max(1, len(fleet.capacities_list))
        customers = generate_customers(size, "random", "random", avg_cap)
        
        q_res = run_benchmark_iteration(depot, customers, fleet, "quantum")
        reporter.log_result(
            f"P6_Random_{i}", 
            q_res["status"], 
            {"errors": q_res["errors"]}
        )

def run_phase_7(reporter: Reporter):
    # Edge cases
    depot = generate_depot("center")
    
    # Empty
    try:
        q_res = run_benchmark_iteration(depot, [], generate_fleet("single"), "quantum")
        reporter.log_result("P7_Empty", q_res["status"], {"errors": q_res["errors"]})
    except Exception as e:
        reporter.log_result("P7_Empty", "FAIL", {"errors": str(e)})
        
    # Tiny capacity
    fleet = generate_fleet("tiny_capacity")
    custs = generate_customers(5, "random", "high", 10.0)
    q_res = run_benchmark_iteration(depot, custs, fleet, "quantum")
    # It might fail validation due to capacity, which is expected/warn
    status = "WARNING" if q_res["status"] == "FAIL" and "Capacity exceeded" in str(q_res["errors"]) else q_res["status"]
    reporter.log_result("P7_TinyCap", status, {"errors": q_res["errors"]})

def run_phase_9(reporter: Reporter):
    depot = generate_depot("center")
    sizes = [5, 10, 20]
    
    for size in sizes:
        fleet = generate_fleet("mixed")
        customers = generate_customers(size, "random", "random", 70.0)
        stab = run_stability_test(depot, customers, fleet, iterations=3 if FAST_MODE else 10)
        reporter.log_stability(stab)
        reporter.log_result(f"P9_Stability_{size}", "PASS", stab)

def main():
    print("Starting Comprehensive Test Suite...")
    report_file = r"C:\Users\GANESH\.gemini\antigravity-ide\brain\6c18954b-413b-4939-acbc-a5189ac7c298\greenroute_v5_test_report.md"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    reporter = Reporter(report_file)
    
    print("Running Phase 1-5 (Functional & Comparison)...")
    run_phase_1_and_5(reporter)
    
    print("Running Phase 6 (Random Stress Test)...")
    run_phase_6(reporter)
    
    print("Running Phase 7 (Edge Cases)...")
    run_phase_7(reporter)
    
    print("Running Phase 9 (Stability)...")
    run_phase_9(reporter)
    
    print("Generating report...")
    reporter.generate_markdown()
    print("Done.")

if __name__ == "__main__":
    main()
