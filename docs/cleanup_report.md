# Repository Cleanup Report

The following directories and files have been identified as unnecessary for source control. They should be ignored by Git (using `.gitignore`) and can be safely removed from future archives.

| Folder / File Pattern | Reason | Estimated Size | Safe to Remove from Git? |
| --- | --- | --- | --- |
| `temp_qiskit_test2/` | Virtual environment, contains downloaded dependencies. | ~150-250 MB | Yes |
| `backend/venv/` | Python virtual environment. | ~100-200 MB | Yes |
| `backend/__pycache__/` | Compiled Python bytecode cache. | ~1-5 MB | Yes |
| `backend/.pytest_cache/` | Pytest internal cache. | < 1 MB | Yes |
| `frontend/node_modules/` | Node.js downloaded dependencies. | ~150-300 MB | Yes |
| `frontend/.next/` | Next.js build output / cache (if applicable). | ~50 MB | Yes |
| `frontend/build/` | React/Vite production build output. | ~10-20 MB | Yes |
| `frontend/dist/` | Vite production build output. | ~10-20 MB | Yes |
| `.idea/`, `.vscode/` | IDE configuration folders. | < 1 MB | Yes |
| `*.log` | Application or system logs. | Variable | Yes |
| `.env` | Contains local secrets/environment variables. | < 1 MB | Yes (from Git, keep local) |

*Note: Do not delete these files from your local workspace unless you are performing a clean install, but they must not be committed to GitHub.*
