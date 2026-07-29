"""
POST /api/upload

Accepts multipart/form-data with:
  - file         : CSV file
  - fleet        : JSON  e.g. '{"Van":2,"Truck":1,"Bike":0,"Electric Van":0}'
  - capacities   : JSON  e.g. '{"Van":50,"Truck":120,"Bike":15,"Electric Van":60}'
"""

import json

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from app.models.vehicle import VehicleConfig
from app.services.dataset import parse_csv
from app.services.demand import check_fleet_capacity
from app.utils.helpers import load_depot

router = APIRouter()


@router.post("/upload")
async def upload_dataset(
    request: Request,
    file: UploadFile = File(...),
    fleet: str      = Form(...),   # JSON: { "Van": 2, "Truck": 1, ... }
    capacities: str = Form(...),   # JSON: { "Van": 50, "Truck": 120, ... }
):
    # --- Parse fleet JSON ---
    try:
        fleet_dict = {k: int(v) for k, v in json.loads(fleet).items()}
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid fleet JSON: {exc}")

    # --- Parse capacities JSON ---
    try:
        cap_dict = {k: float(v) for k, v in json.loads(capacities).items()}
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid capacities JSON: {exc}")

    # --- Validate vehicle config ---
    try:
        v_config = VehicleConfig(fleet=fleet_dict, capacities=cap_dict)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # --- Read and validate CSV ---
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        customers, clustering_notice = parse_csv(contents)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # --- Load depot ---
    try:
        depot = load_depot()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # --- Persist ---
    request.app.state.customers = customers
    request.app.state.vehicle_config = v_config
    request.app.state.depot = depot
    request.app.state.classical_result = None
    request.app.state.quantum_result = None
    request.app.state.classical_routes = None
    request.app.state.quantum_routes = None
    request.app.state.dist_matrix = None

    # --- Demand / capacity pre-check ---
    fleet_check = check_fleet_capacity(customers, v_config)

    return {
        "message": "Dataset loaded successfully.",
        "customers": len(customers),
        "clustering_notice": clustering_notice,
        "depot": {"lat": depot.latitude, "lng": depot.longitude},
        "vehicle_config": {
            "fleet": v_config.fleet,
            "capacities": v_config.capacities,
            "total_count": v_config.total_count,
            "blended_fuel_rate": v_config.blended_fuel_rate,
            "dominant_type": v_config.dominant_type,
        },
        "fleet_check": fleet_check,
    }
