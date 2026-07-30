import logging
from typing import List
from fastapi import HTTPException

from app import config
from app.models.customer import Customer
from app.models.depot import Depot
from app.models.vehicle import VehicleConfig
from app.services.base_solver import BaseQuantumSolver
from app.services.qaoa_solver import QAOASolver
from app.services.bqphy_solver import BQPhySolver
from app.services.quantum_result import QuantumResult

logger = logging.getLogger(__name__)

SOLVERS = {
    "qaoa": QAOASolver,
    "bqphy": BQPhySolver,
}

def get_solver() -> BaseQuantumSolver:
    """
    Retrieves the configured quantum solver instance.
    """
    backend_name = getattr(config, "QUANTUM_SOLVER_BACKEND", "qaoa").lower()
    
    if backend_name not in SOLVERS:
        logger.warning(f"Unknown solver backend '{backend_name}'. Falling back to 'qaoa'.")
        backend_name = "qaoa"
        
    logger.info(f"Using quantum solver backend: {backend_name}")
    
    solver_class = SOLVERS[backend_name]
    return solver_class()

def solve_quantum(
    depot: Depot,
    customers: List[Customer],
    vehicle_config: VehicleConfig,
    bypass_clustering: bool = False,
) -> QuantumResult:
    """
    Factory wrapper to match the exact API signature of the original solve_quantum.
    Instantiates the correct solver via configuration and delegates the call.
    """
    try:
        solver = get_solver()
        return solver.solve(depot, customers, vehicle_config, bypass_clustering)
    except Exception as e:
        logger.error(f"Solver execution failed: {e}")
        # Re-raise as HTTPException so FastAPI doesn't crash but cleanly returns a 500
        raise HTTPException(status_code=500, detail=str(e))
