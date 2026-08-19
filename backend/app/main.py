"""
main.py — FastAPI application entry point (v2.1.0).

Run with:
    uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import classical, compare, quantum, upload
from app.routes import benchmark, analytics, fleet, reset, convergence

app = FastAPI(
    title="GreenRoute API",
    description="Quantum Assisted Capacitated Vehicle Routing — QT-6.22 v7.2",
    version="7.2.0",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory application state
# ---------------------------------------------------------------------------
app.state.customers         = None
app.state.vehicle_config    = None
app.state.depot             = None
app.state.classical_result  = None
app.state.quantum_result    = None
app.state.classical_routes  = None   # v2: stored for analytics
app.state.quantum_routes    = None   # v2: stored for analytics
app.state.dist_matrix       = None   # v2: stored for analytics

# ---------------------------------------------------------------------------
# v1 Routers (unchanged)
# ---------------------------------------------------------------------------
app.include_router(upload.router,    prefix="/api", tags=["Upload"])
app.include_router(classical.router, prefix="/api", tags=["Classical"])
app.include_router(quantum.router,   prefix="/api", tags=["Quantum"])
app.include_router(compare.router,   prefix="/api", tags=["Compare"])

# ---------------------------------------------------------------------------
# v2 Routers (new)
# ---------------------------------------------------------------------------
app.include_router(benchmark.router,   prefix="/api", tags=["Benchmark"])
app.include_router(analytics.router,   prefix="/api", tags=["Analytics"])
app.include_router(fleet.router,       prefix="/api", tags=["Fleet"])
app.include_router(reset.router,       prefix="/api", tags=["Reset"])
app.include_router(convergence.router, prefix="/api", tags=["Convergence"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": app.version}
