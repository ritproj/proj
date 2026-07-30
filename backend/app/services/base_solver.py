from abc import ABC, abstractmethod
from typing import List

from app.models.customer import Customer
from app.models.depot import Depot
from app.models.vehicle import VehicleConfig
from app.services.quantum_result import QuantumResult

class BaseQuantumSolver(ABC):
    @abstractmethod
    def solve(
        self,
        depot: Depot,
        customers: List[Customer],
        vehicle_config: VehicleConfig,
        bypass_clustering: bool = False,
    ) -> QuantumResult:
        """
        Solve the Capacitated Vehicle Routing Problem (CVRP) for the given inputs.
        """
        pass
