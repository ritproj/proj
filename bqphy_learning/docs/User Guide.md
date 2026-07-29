<!--
    Document: BQPhy Python Library Documentation
    Creator: HPC Team
    Date: January 31, 2026
    Version: Preview 1.0
    Description: Complete user guide for installing, configuring, and using the BQPhy Python Library for quantum-inspired optimization
-->
# BQPhy Python Library User Guide

## Table of Contents

1. [Python Integration Strategy](#python-integration-strategy)
2. [Package Architecture and Structure](#package-architecture-and-structure)
   - [Library Organization](#library-organization)
   - [Prerequisites](#prerequisites)
3. [Installation Procedure](#installation-procedure)
   - [Installation of library on Windows Powershell](#installation-of-library-on-windows-powershell)
     - [Step-by-Step Installation](#step-by-step-installation)
     - [License Configuration](#license-configuration)
     - [Verification and Testing](#verification-and-testing)
     - [Troubleshooting Common Issues](#troubleshooting-common-issues)
     - [Uninstallation of BQPhy Library](#uninstallation-of-bqphy-library)
   - [Installation of library on Linux Terminal](#installation-of-library-on-linux-terminal)
     - [Step-by-Step Installation](#step-by-step-installation-1)
     - [License Configuration](#license-configuration-1)
     - [Verification and Testing](#verification-and-testing-1)
     - [Troubleshooting Common Issues](#troubleshooting-common-issues-1)
     - [Uninstallation of BQPhy Library](#uninstallation-of-bqphy-library-1)
4. [Usage Patterns and API Design](#usage-patterns-and-api-design)
   - [Basic Usage Pattern](#basic-usage-pattern)
   - [Function Interface Specifications](#function-interface-specifications)
     - [Objective Function Requirements](#objective-function-requirements)
     - [Objective Function Implementation Patterns](#objective-function-implementation-patterns)
   - [Constraint Handling Framework](#constraint-handling-framework)
     - [Constraint Function Structure](#constraint-function-structure)
     - [Practical Constraint Examples](#practical-constraint-examples)
   - [Parameter Configuration](#parameter-configuration)
     - [Core Algorithm Parameters](#core-algorithm-parameters)
     - [Convergence Criteria Configuration](#convergence-criteria-configuration)
     - [Optimization Control and Termination (Kill Switch)](#optimization-control-and-termination-kill-switch)
     - [Initial Population Seeding Configuration](#initial-population-seeding-configuration)
     - [Restart and Recovery Features](#restart-and-recovery-features)
       - [Restart Dump Configuration](#restart-dump-configuration)
       - [Restart Solver Configuration](#restart-solver-configuration)
     - [Variable Bounds Specification](#variable-bounds-specification)
     - [Logging and Output Configuration](#logging-and-output-configuration)
5. [Performance Optimization Guidelines](#performance-optimization-guidelines)
   - [Vectorization Best Practices](#vectorization-best-practices)
   - [Memory Management](#memory-management)
6. [Output Interpretation](#output-interpretation)
   - [Standard Output Structure](#standard-output-structure)
   - [Results Analysis](#results-analysis)
7. [Environment Configuration](#environment-configuration)
   - [Creating Virtual Environment](#creating-virtual-environment)
     - [Linux Virtual Environment Setup](#linux-virtual-environment-setup)
     - [Windows Virtual Environment Setup](#windows-virtual-environment-setup)
8. [Usage Examples](#usage-examples)
   - [Continuous Optimization Example](#continuous-optimization-example)
     - [Sample 1: Rastrigin Function](#sample-1-rastrigin-function)
   - [Binary Optimization Example](#binary-optimization-example)
     - [Sample 2: 0/1 Knapsack Problem](#sample-2-01-knapsack-problem)
9. [Conclusion](#conclusion)
   - [Documentation Coverage Summary](#documentation-coverage-summary)
   - [Best Practices for Success](#best-practices-for-success)
   - [Final Considerations](#final-considerations)
10. [Getting Help](#getting-help)

---

## Python Integration Strategy

The Python integration strategy represents the sophisticated interface layer that transforms BQPhy's high-performance C++ core into a native Python experience through advanced binding techniques that seamlessly integrate with the broader Python scientific computing ecosystem. This comprehensive integration approach leverages pybind11's modern C++ binding capabilities to provide automatic type conversion between native C++ data structures and Python's NumPy arrays, enabling users to pass familiar Python data types (lists, dictionaries, numpy arrays) directly to optimization functions without manual marshaling or performance penalties. The strategy implements intelligent exception mapping that translates C++ exceptions into appropriate Python exception hierarchies with detailed error messages and stack traces, while maintaining strict type safety through automatic parameter validation and comprehensive input verification. 

The integration includes automatic detection and binding of Python callable objects as objective functions, enabling users to define optimization targets using standard Python syntax with full access to the Python ecosystem including scientific libraries like SciPy, pandas, and matplotlib for pre- and post-processing. This approach ensures that Python users can leverage BQPhy's advanced quantum-inspired optimization capabilities using familiar Python programming patterns and data structures, while the underlying algorithm execution maintains the full performance characteristics of the optimized C++ implementation, effectively combining Python's ease of use with C++ computational efficiency in a transparent and user-friendly interface that requires no knowledge of cross-language programming or manual data conversion processes.

## Package Architecture and Structure

The BQPhy Python Library provides a comprehensive optimization environment that seamlessly integrates with Python's scientific computing ecosystem, offering both high-level convenience functions and low-level performance optimization capabilities through a carefully structured package hierarchy.

### Library Organization

The library follows Python's standard package organization principles, providing clear separation between user interfaces, examples, and core functionality. The components of the library, distributed as a wheel package titled *BQPhyLibrary_v<x>.<y>.<z>.whl* , are as follows:

├── main.mexw64                         


```plaintext
bqphy/
├── __init__.py                         # Package initialization and exports
├── BQPhy_Optimiser.so                  # Compiled C++ source code (for Linux)
OR
├── BQPhy_Optimiser.pyd                 # Compiled C++ source code (for Windows)
├── examples/                           # Sample scripts and demonstrations  
│   ├── continuous_rastrigin.py         # Continuous optimization example
│   └── binary_knapsack.py              # Binary optimization example
└── docs/                               # Documentation and user guides
│   └── User Guide.md                   # User guide for running BQPhy python library
│   └── Special Note.md                 # Special notes to User for troubleshooting
```

The Core Components of this packaged library are as follows,

**Main Optimization Interface**
The `BQPhy_Optimiser` class serves as the primary entry point for optimization tasks, providing a Python-native interface that accepts standard Python data structures (dictionaries, lists, NumPy arrays) while leveraging the high-performance C++ core through pybind11 integration.

**Pybind11 Integration Layer**
The compiled binary module contains the quantum-inspired optimization algorithms, providing near-native C++ performance while maintaining full integration with Python's memory management and error handling systems.

**Example Repository**
The examples directory provides comprehensive demonstrations of both continuous and binary optimization scenarios, serving as both learning resources and templates for user applications.

### Prerequisites

Before installing and using the BQPhy Python Library, ensure your system meets the following requirements:

**Python Version Requirements**
- **Supported Python Versions**: 3.10 or 3.12 only
- **Architecture**: x86_64 (64-bit) architecture required
- **Important**: The wheel package is compiled specifically for Python 3.10 and 3.12. Other Python versions (3.8, 3.9, 3.11, 3.13+) are not currently supported

**System Requirements**

*Linux Systems*
- **GLIBC Version**: 2.32 or higher required for proper C++ library compatibility
- **Distribution Compatibility**: 
  - Ubuntu 20.04+ (GLIBC 2.31+, upgrade to 2.32+ required)
  - Ubuntu 22.04+ (GLIBC 2.35+) ✓ Recommended
  - CentOS Stream 9+ (GLIBC 2.34+) ✓
  - RHEL 9+ (GLIBC 2.34+) ✓
  - Fedora 35+ (GLIBC 2.34+) ✓
  - Debian 11+ (GLIBC 2.31+, may require upgrade)
- **Memory**: Minimum 2GB RAM (4GB+ recommended for large-scale optimizations)
- **Disk Space**: At least 200MB free space for virtual environment and dependencies

*Windows Systems*
- **Operating System**: Windows 10/11 (64-bit)
- **Visual C++ Runtime**: Microsoft Visual C++ Redistributable 2019 or later
- **Memory**: Minimum 2GB RAM (4GB+ recommended)
- **Disk Space**: At least 200MB free space

**Python Dependencies**
- **NumPy**: Automatically installed with the wheel package
- **pip**: Version 21.0+ recommended for wheel installation
- **venv**: Python virtual environment module (included with Python 3.10+)

## Installation Procedure

The installatoin procedure of the BQPhy Library is fairly straighforward and quick. 

### Installation of library on Windows Powershell

The Windows PowerShell installation method provides a command-line approach for installing the BQPhy Python Library using Windows' native PowerShell environment with comprehensive error handling and verification procedures.

#### Step-by-Step Installation

**Step 1: Open PowerShell**

1. **Launch PowerShell as Administrator (Recommended):**
   - Press `Win + X` and select "Terminal (Admin)"
   - Or search "PowerShell" in Start menu, right-click and "Run as Administrator"
   - Or press `Win + R`, type `powershell`, then press `Ctrl + Shift + Enter`

2. **Alternative: Regular User PowerShell:**
   ```powershell
   # Press Win + R, type 'powershell' and press Enter
   # Or search 'PowerShell' in Start menu
   ```

**Step 2: Verify Python Installation**

```powershell
# Check Python version (must be 3.10 or 3.12)
python --version
# or
python3 --version

# Check pip availability
pip --version

# Verify architecture (should show AMD64 for x86_64)
[System.Environment]::Is64BitProcess
# Should return True
```

Expected output:
```
Python 3.12.x
pip 23.x.x from...
True
```

**Step 3: Create Project Directory**

```powershell
# Navigate to your desired location
cd C:\Users\$env:USERNAME\Documents

# Create project directory
New-Item -ItemType Directory -Name "BQPhy_Project" -Force
Set-Location BQPhy_Project

# Verify current location
Get-Location
```

**Step 4: Create Virtual Environment**

```powershell
# Create virtual environment using Python 3.10 or 3.12
python -m venv .BQP_Env

# Alternative if you have multiple Python versions
# python3.12 -m venv .BQP_Env

# Verify virtual environment creation
if (Test-Path ".BQP_Env\Scripts\activate.ps1") {
    Write-Host "✓ Virtual environment created successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Virtual environment creation failed" -ForegroundColor Red
    exit 1
}
```

**Step 5: Activate Virtual Environment**

```powershell
# Set execution policy if needed (first time only)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Activate the virtual environment
.BQP_Env\Scripts\Activate.ps1

# Verify activation - your prompt should show (.BQP_Env)
# Check Python executable location
(Get-Command python).Source
# Should show path inside .BQP_Env\Scripts
```

**Step 6: Upgrade pip (Recommended)**

```powershell
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Verify pip upgrade
pip --version
```

**Step 7: Install BQPhy Library**

```powershell
# Method 1: Install from local wheel file
# (Place your BQPhyLibrary_v*.whl file in the current directory)
pip install BQPhyLibrary_v1.0.0.whl

# Method 2: Install with full path to wheel file
# pip install "C:\path\to\your\BQPhyLibrary_v1.0.0.whl"

# Method 3: Install from current directory if wheel is present
# pip install *.whl
```
#### License Configuration 

The BQPhy Python Library requires a valid license file to function properly. The license configuration process is straightforward and follows these steps:

**Step 1: Initial Run and License Folder Creation**

When you first attempt to use BQPhy, the library will automatically detect the absence of a license and create the necessary license directory structure.

```powershell
# Run a simple test to trigger license folder creation
python -c @"
import bqphy.BQPhy_Optimiser as qea
print('Testing BQPhy import...')
try:
    optimizer = qea.BQPhy_OPTIMISER()
    print('License check in progress...')
except Exception as e:
    print(f'Expected license error: {e}')
    print('License folder should now be created.')
"@
```

Expected output:
```
Testing BQPhy import...
License check in progress...
Expected license error: License file not found. Please contact BQP for license.
License folder should now be created.
```

**Step 2: Locate the License Directory**

The license folder will be created in the same location as the compiled .so/.pyd files within your virtual environment:

```powershell
# Find the BQPhy installation directory
$bqphyPath = python -c "import bqphy; import os; print(os.path.dirname(bqphy.__file__))"
Write-Host "BQPhy installed at: $bqphyPath"

# Check for license directory
$licenseDir = Join-Path $bqphyPath "license"
if (Test-Path $licenseDir) {
    Write-Host "✓ License directory found: $licenseDir" -ForegroundColor Green
    Get-ChildItem $licenseDir
} else {
    Write-Host "⚠ License directory not found. Run BQPhy once to create it." -ForegroundColor Yellow
}
```

**Step 3: Contact BQP Executive for License File**

Once the license directory is created:

1. **Contact Information**: Reach out to your designated BQP executive or support contact
2. **Provide Details**: Share your system information and intended use case
3. **Receive License**: You will receive a `.dat` file containing your license

**Step 4: Install License File**

```powershell
# Navigate to the license directory
$licenseDir = python -c "import bqphy; import os; print(os.path.join(os.path.dirname(bqphy.__file__), 'license'))"
Set-Location $licenseDir
Write-Host "Current license directory: $(Get-Location)"

# Copy your provided license file here
# Example: Copy-Item "C:\Downloads\your_license.dat" -Destination "."
# The license file should be named exactly as provided by BQP

# Verify license file placement
Get-ChildItem *.dat
if ($?) {
    Write-Host "✓ License file found in directory" -ForegroundColor Green
} else {
    Write-Host "✗ No .dat license file found" -ForegroundColor Red
    Write-Host "Please ensure you've copied the license file to: $licenseDir"
}
```

**Step 5: Verify License Installation**

```powershell
# Test license validation
python -c @"
import bqphy.BQPhy_Optimiser as qea
import numpy as np

print('Testing BQPhy with license...')
try:
    optimizer = qea.BQPhy_OPTIMISER()
    print('✓ License validation successful!')
    print('✓ BQPhy is ready for use')
    
    # Quick functionality test
    config = {
        'numPopulation': 10,
        'maxGeneration': 5,
        'designVariables': 2,
        'typeOfOptimisation': 'CONTINUOUS',
        'lowerBounds': [-1.0, -1.0],
        'upperBounds': [1.0, 1.0]
    }
    
    def simple_test(x):
        return np.sum(x**2, axis=1)
    
    optimizer.initialize(config)
    optimizer.model(simple_test)
    optimizer.runOptimization()
    print('✓ License verification complete - BQPhy is fully functional!')
    
except Exception as e:
    print(f'✗ License validation failed: {e}')
    print('Please check:')
    print('1. License file is in the correct directory')
    print('2. License file is not corrupted')
    print('3. License is valid and not expired')
    print('4. Contact BQP support if issues persist')
"@
```

**Troubleshooting License Issues**

```powershell
# Check license directory structure
$bqphyRoot = python -c "import bqphy; import os; print(os.path.dirname(bqphy.__file__))"
Write-Host "BQPhy installation structure:"
Get-ChildItem $bqphyRoot -Recurse | Where-Object { $_.Name -like "*license*" -or $_.Name -like "*.dat" }

# Verify file permissions
$licenseDir = Join-Path $bqphyRoot "license"
if (Test-Path $licenseDir) {
    Write-Host "License directory permissions:"
    Get-Acl $licenseDir | Format-List
}

# Check for common issues
Write-Host "License troubleshooting checklist:"
Write-Host "1. License directory exists: $(Test-Path $licenseDir)"
Write-Host "2. License file present: $(Test-Path $licenseDir\*.dat)"
Write-Host "3. Virtual environment active: $($env:VIRTUAL_ENV -ne $null)"
```

#### Verification and Testing

```powershell
# Check installed packages
pip list | Select-String "bqphy"

# Test basic import
python -c "import bqphy.BQPhy_Optimiser as qea; print('✓ BQPhy successfully imported!')"

# Advanced verification
python -c @"
import bqphy.BQPhy_Optimiser as qea
import numpy as np
print('BQPhy Library Information:')
print('- Import successful: ✓')
print('- NumPy available: ✓')
optimizer = qea.BQPhy_OPTIMISER()
print('- Optimizer creation: ✓')
print('Installation verification complete!')
"@
```

**Test with Simple Example**

```powershell
# Create and run a simple test script
$testScript = @"
import numpy as np
import bqphy.BQPhy_Optimiser as qea

def simple_objective(x):
    return np.sum(x**2, axis=1)

config = {
    'numPopulation': 20,
    'maxGeneration': 10,
    'designVariables': 2,
    'typeOfOptimisation': 'CONTINUOUS',
    'lowerBounds': [-5.0, -5.0],
    'upperBounds': [5.0, 5.0]
}

optimizer = qea.BQPhy_OPTIMISER()
optimizer.initialize(config)
optimizer.model(simple_objective)
optimizer.runOptimization()
best_solution, fitness_history = optimizer.getBestDesign()

print(f'Best solution: {best_solution}')
print(f'Best fitness: {fitness_history[-1]:.6f}')
print('✓ BQPhy installation test completed successfully!')
"@

# Save and run test script
$testScript | Out-File -FilePath "test_bqphy.py" -Encoding UTF8
python test_bqphy.py
```

#### Troubleshooting Common Issues

**Execution Policy Issues**
```powershell
# If you get execution policy errors:
Get-ExecutionPolicy -List
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# For persistent solution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

**Path Issues**
```powershell
# If Python is not found:
$env:PATH -split ';' | Select-String "Python"

# Add Python to PATH if needed:
$pythonPath = "C:\Python312;C:\Python312\Scripts"
[System.Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";" + $pythonPath, [System.EnvironmentVariableTarget]::User)
```

**Virtual Environment Activation Issues**
```powershell
# If activation fails, try:
& ".BQP_Env\Scripts\Activate.ps1"

# Or use Command Prompt style:
.BQP_Env\Scripts\activate.bat
```

**Cleanup Commands**
```powershell
# Deactivate virtual environment
deactivate

# Remove virtual environment (if needed)
Remove-Item -Recurse -Force .BQP_Env

# Remove test files
Remove-Item test_bqphy.py
```

#### Uninstallation of BQPhy Library

When you need to remove the BQPhy Python Library from your system, follow these steps to ensure complete cleanup of all components and virtual environment.

**Step 1: Deactivate Virtual Environment**

If you currently have the BQPhy virtual environment active, deactivate it first:

```powershell
# Windows PowerShell
deactivate
```

```bash
# Linux Terminal  
deactivate
```

**Step 2: Uninstall BQPhy Package**

Before removing the virtual environment, you can uninstall just the BQPhy package if needed:

```powershell
# Windows PowerShell - Activate environment first
.BQP_Env\Scripts\Activate.ps1
pip uninstall bqphy -y
deactivate
```

```bash
# Linux Terminal - Activate environment first
source .BQP_Env/bin/activate
pip uninstall bqphy -y
deactivate
```

**Step 3: Remove Virtual Environment**

Remove the entire virtual environment directory and all its contents:

```powershell
# Windows PowerShell
Remove-Item -Recurse -Force .BQP_Env
if (!(Test-Path .BQP_Env)) {
    Write-Host "✓ Virtual environment removed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to remove virtual environment" -ForegroundColor Red
}
```

```bash
# Linux Terminal
rm -rf .BQP_Env
if [ ! -d ".BQP_Env" ]; then
    echo "✓ Virtual environment removed successfully"
else
    echo "✗ Failed to remove virtual environment"
fi
```

**Step 4: Clean Up Project Files**

Remove any test files, example scripts, or project directories created during installation:

```powershell
# Windows PowerShell - Remove test files
Remove-Item -Force test_bqphy.py -ErrorAction SilentlyContinue
Remove-Item -Force *.whl -ErrorAction SilentlyContinue

# Remove entire project directory (optional)
cd ..
Remove-Item -Recurse -Force BQPhy_Project -ErrorAction SilentlyContinue
```

```bash
# Linux Terminal - Remove test files  
rm -f test_bqphy.py
rm -f *.whl

# Remove entire project directory (optional)
cd ..
rm -rf BQPhy_Project
```

**Step 5: Verification**

Verify that BQPhy has been completely removed:

```powershell
# Windows PowerShell - Check for remaining files
Get-ChildItem -Recurse -Name "*bqphy*" -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Name "*.whl" -ErrorAction SilentlyContinue

# Should return no results if completely removed
```

```bash
# Linux Terminal - Check for remaining files
find . -name "*bqphy*" 2>/dev/null
find . -name "*.whl" 2>/dev/null

# Should return no results if completely removed
```

**Step 6: System Cleanup (Optional)**

For complete system cleanup, you may also want to:

```powershell
# Windows PowerShell - Clear pip cache
pip cache purge

# Reset PowerShell execution policy (if changed during installation)
Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser
```

```bash
# Linux Terminal - Clear pip cache
pip cache purge

# Clear any downloaded packages
rm -rf ~/.cache/pip/wheels/bqphy*
```

**Verification Commands**

To confirm complete removal:

```powershell
# Windows PowerShell
python -c "try: import bqphy; print('BQPhy still installed') except ImportError: print('✓ BQPhy successfully removed')"
```

```bash
# Linux Terminal
python3 -c "try: import bqphy; print('BQPhy still installed') except ImportError: print('✓ BQPhy successfully removed')"
```

**Troubleshooting Uninstallation**

If you encounter issues during uninstallation:

1. **Permission Denied Errors**:
   ```powershell
   # Windows - Run PowerShell as Administrator
   rm .BQP_Env
   ```
2. **Files in Use**:
   - Close all Python processes and IDEs
   - Restart your terminal/command prompt
   - Retry the removal commands

3. **Incomplete Removal**:
   ```powershell
   # Windows - Manual cleanup
   $env:LOCALAPPDATA + "\pip\cache"  # Check pip cache location
   ```

The BQPhy library and all associated files should now be completely removed from your system.

---

### Installation of library on Linux Terminal

The Linux Terminal installation method provides a command-line approach for installing the BQPhy Python Library using Linux's native shell environment with comprehensive dependency checking and system compatibility verification.

#### Step-by-Step Installation

**Step 1: Open Terminal**

```bash
# Method 1: Keyboard shortcut
# Press Ctrl + Alt + T

# Method 2: From GUI
# Search for "Terminal" in application launcher

# Method 3: From file manager
# Right-click in folder and select "Open in Terminal"
```

**Step 2: System Compatibility Check**

```bash
# Check Python version (must be 3.10 or 3.12)
python3 --version
# or
python3.12 --version  # if specifically installed

# Check architecture (must be x86_64)
uname -m
# Should return: x86_64

# Check GLIBC version (must be 2.32+)
ldd --version | head -1
# Should show: ldd (GNU libc) 2.32 or higher

# Alternative GLIBC check
getconf GNU_LIBC_VERSION
```

Expected output:
```bash
Python 3.12.x
x86_64
ldd (GNU libc) 2.35
glibc 2.35
```

**Step 3: Install Python Dependencies (if needed)**

*Ubuntu/Debian Systems:*
```bash
# Update package lists
sudo apt update

# Install Python 3.12 and related packages
sudo apt install -y python3.12 python3.12-venv python3.12-pip python3.12-dev

# For older Ubuntu versions, use deadsnakes PPA:
# sudo add-apt-repository ppa:deadsnakes/ppa
# sudo apt update
# sudo apt install python3.12 python3.12-venv python3.12-pip
```

*RHEL/CentOS/Fedora Systems:*
```bash
# For Fedora
sudo dnf install -y python3.12 python3.12-pip python3.12-devel

# For RHEL/CentOS 8+
sudo dnf install -y python3.12 python3.12-pip python3.12-devel

# For older RHEL/CentOS 7
sudo yum install -y python3.12 python3.12-pip python3.12-devel
```

**Step 4: Create Project Directory**

```bash
# Navigate to your home directory
cd ~

# Create project directory
mkdir -p BQPhy_Project
cd BQPhy_Project

# Verify current directory
pwd
# Should show: /home/username/BQPhy_Project
```

**Step 5: Create Virtual Environment**

```bash
# Create virtual environment using Python 3.12
python3.12 -m venv .BQP_Env

# Alternative for systems with python3.10
# python3.10 -m venv .BQP_Env

# Verify virtual environment creation
if [ -d ".BQP_Env" ] && [ -f ".BQP_Env/bin/activate" ]; then
    echo "✓ Virtual environment created successfully"
else
    echo "✗ Virtual environment creation failed"
    exit 1
fi
```

**Step 6: Activate Virtual Environment**

```bash
# Activate the virtual environment
source .BQP_Env/bin/activate

# Verify activation - your prompt should show (.BQP_Env)
# Check Python executable location
which python
# Should show: /path/to/BQPhy_Project/.BQP_Env/bin/python

# Verify Python version in virtual environment
python --version
```

**Step 7: Upgrade pip (Recommended)**

```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Verify pip upgrade
pip --version
```

**Step 8: Install BQPhy Library**

```bash
# Method 1: Install from local wheel file
# (Place your BQPhyLibrary_v*.whl file in the current directory)
pip install BQPhyLibrary_v1.0.0.whl

# Method 2: Install with full path to wheel file
# pip install "/path/to/your/BQPhyLibrary_v1.0.0.whl"

# Method 3: Install from current directory if wheel is present
# pip install *.whl

# Method 4: Install with verbose output for debugging
# pip install -v BQPhyLibrary_v1.0.0.whl
```

#### License Configuration

The BQPhy Python Library requires a valid license file to function properly. The license configuration process is straightforward and follows these steps:

**Step 1: Initial Run and License Folder Creation**

When you first attempt to use BQPhy, the library will automatically detect the absence of a license and create the necessary license directory structure.

```bash
# Run a simple test to trigger license folder creation
python << 'EOF'
import bqphy.BQPhy_Optimiser as qea
print('Testing BQPhy import...')
try:
    optimizer = qea.BQPhy_OPTIMISER()
    print('License check in progress...')
except Exception as e:
    print(f'Expected license error: {e}')
    print('License folder should now be created.')
EOF
```

Expected output:
```
Testing BQPhy import...
License check in progress...
Expected license error: License file not found. Please contact BQP for license.
License folder should now be created.
```

**Step 2: Locate the License Directory**

The license folder will be created in the same location as the compiled .so files within your virtual environment:

```bash
# Find the BQPhy installation directory
BQPHY_PATH=$(python -c "import bqphy; import os; print(os.path.dirname(bqphy.__file__))")
echo "BQPhy installed at: $BQPHY_PATH"

# Check for license directory
LICENSE_DIR="$BQPHY_PATH/license"
if [ -d "$LICENSE_DIR" ]; then
    echo "✓ License directory found: $LICENSE_DIR"
    ls -la "$LICENSE_DIR"
else
    echo "⚠ License directory not found. Run BQPhy once to create it."
fi
```

**Step 3: Contact BQP Executive for License File**

Once the license directory is created:

1. **Contact Information**: Reach out to your designated BQP executive or support contact
2. **Provide Details**: Share your system information and intended use case
3. **Receive License**: You will receive a `.dat` file containing your license

**Step 4: Install License File**

```bash
# Navigate to the license directory
LICENSE_DIR=$(python -c "import bqphy; import os; print(os.path.join(os.path.dirname(bqphy.__file__), 'license'))")
cd "$LICENSE_DIR"
echo "Current license directory: $(pwd)"

# Copy your provided license file here
# Example: cp ~/Downloads/your_license.dat .
# The license file should be named exactly as provided by BQP

# Verify license file placement
if ls *.dat 1> /dev/null 2>&1; then
    echo "✓ License file found in directory:"
    ls -la *.dat
else
    echo "✗ No .dat license file found"
    echo "Please ensure you've copied the license file to: $LICENSE_DIR"
fi
```

**Step 5: Verify License Installation**

```bash
# Test license validation
python << 'EOF'
import bqphy.BQPhy_Optimiser as qea
import numpy as np

print('Testing BQPhy with license...')
try:
    optimizer = qea.BQPhy_OPTIMISER()
    print('✓ License validation successful!')
    print('✓ BQPhy is ready for use')
    
    # Quick functionality test
    config = {
        'numPopulation': 10,
        'maxGeneration': 5,
        'designVariables': 2,
        'typeOfOptimisation': 'CONTINUOUS',
        'lowerBounds': [-1.0, -1.0],
        'upperBounds': [1.0, 1.0]
    }
    
    def simple_test(x):
        return np.sum(x**2, axis=1)
    
    optimizer.initialize(config)
    optimizer.model(simple_test)
    optimizer.runOptimization()
    print('✓ License verification complete - BQPhy is fully functional!')
    
except Exception as e:
    print(f'✗ License validation failed: {e}')
    print('Please check:')
    print('1. License file is in the correct directory')
    print('2. License file is not corrupted')
    print('3. License is valid and not expired')
    print('4. Contact BQP support if issues persist')
EOF
```

**Troubleshooting License Issues**

```bash
# Check license directory structure
BQPHY_ROOT=$(python -c "import bqphy; import os; print(os.path.dirname(bqphy.__file__))")
echo "BQPhy installation structure:"
find "$BQPHY_ROOT" -name "*license*" -o -name "*.dat" -type f -o -type d

# Verify file permissions
LICENSE_DIR="$BQPHY_ROOT/license"
if [ -d "$LICENSE_DIR" ]; then
    echo "License directory permissions:"
    ls -ld "$LICENSE_DIR"
    if [ "$(ls -A $LICENSE_DIR)" ]; then
        echo "License directory contents:"
        ls -la "$LICENSE_DIR"
    else
        echo "License directory is empty"
    fi
fi

# Check for common issues
echo "License troubleshooting checklist:"
echo "1. License directory exists: $([ -d "$LICENSE_DIR" ] && echo 'Yes' || echo 'No')"
echo "2. License file present: $([ -f "$LICENSE_DIR"/*.dat ] && echo 'Yes' || echo 'No')"
echo "3. Virtual environment active: $([ -n "$VIRTUAL_ENV" ] && echo 'Yes' || echo 'No')"
echo "4. Current user: $(whoami)"
echo "5. License directory writable: $([ -w "$LICENSE_DIR" ] && echo 'Yes' || echo 'No')"

# Fix common permission issues
if [ -d "$LICENSE_DIR" ] && [ ! -w "$LICENSE_DIR" ]; then
    echo "Fixing license directory permissions..."
    chmod 755 "$LICENSE_DIR"
    echo "License directory permissions updated"
fi
```

#### Verification and Testing

```bash
# Check installed packages
pip list | grep -i bqphy

# Test basic import
python -c "import bqphy.BQPhy_Optimiser as qea; print('✓ BQPhy successfully imported!')"

# Advanced verification script
python << 'EOF'
import bqphy.BQPhy_Optimiser as qea
import numpy as np

print("BQPhy Library Information:")
print("- Import successful: ✓")
print("- NumPy available: ✓")

try:
    optimizer = qea.BQPhy_OPTIMISER()
    print("- Optimizer creation: ✓")
    print("Installation verification complete!")
except Exception as e:
    print(f"- Optimizer creation failed: {e}")
EOF
```

**Test with Simple Example**

```bash
# Create a simple test script
cat > test_bqphy.py << 'EOF'
import numpy as np
import bqphy.BQPhy_Optimiser as qea

def simple_objective(x):
    return np.sum(x**2, axis=1)

config = {
    'numPopulation': 20,
    'maxGeneration': 10,
    'designVariables': 2,
    'typeOfOptimisation': 'CONTINUOUS',
    'lowerBounds': [-5.0, -5.0],
    'upperBounds': [5.0, 5.0]
}

print("Running BQPhy test optimization...")
optimizer = qea.BQPhy_OPTIMISER()
optimizer.initialize(config)
optimizer.model(simple_objective)
optimizer.runOptimization()
best_solution, fitness_history = optimizer.getBestDesign()

print(f'Best solution: {best_solution}')
print(f'Best fitness: {fitness_history[-1]:.6f}')
print('✓ BQPhy installation test completed successfully!')
EOF

# Run the test script
python test_bqphy.py
```

#### Troubleshooting Common Issues

**Python Version Issues**
```bash
# If python3.12 is not found, check available versions:
ls /usr/bin/python*

# Install from deadsnakes PPA (Ubuntu/Debian):
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-pip
```

**GLIBC Version Issues**
```bash
# Check detailed GLIBC version
/lib/x86_64-linux-gnu/libc.so.6

# If GLIBC is too old, consider:
# 1. Upgrading your Linux distribution
# 2. Using Docker with compatible base image
# 3. Building from source (advanced users)

# Docker alternative:
echo "FROM ubuntu:22.04
RUN apt update && apt install -y python3.12 python3.12-pip python3.12-venv
WORKDIR /app" > Dockerfile
```

**Permission Issues**
```bash
# If you get permission errors:
sudo chown -R $USER:$USER ~/.local
sudo chown -R $USER:$USER BQPhy_Project

# For system-wide installation issues:
sudo apt update
sudo apt install python3.12-dev build-essential
```

**Virtual Environment Issues**
```bash
# If virtual environment activation fails:
ls -la .BQP_Env/bin/

# Re-create virtual environment:
rm -rf .BQP_Env
python3.12 -m venv .BQP_Env
source .BQP_Env/bin/activate
```

**Library Import Issues**
```bash
# Check library location:
find .BQP_Env -name "*bqphy*" -type f

# Check Python import path:
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall library:
pip uninstall bqphy
pip install BQPhyLibrary_v1.0.0.whl
```

**Cleanup Commands**
```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment (if needed)
rm -rf .BQP_Env

# Remove test files
rm -f test_bqphy.py

# Remove entire project directory (if needed)
cd ..
rm -rf BQPhy_Project
```

**System Resource Monitoring**
```bash
# Monitor installation process:
htop  # or top

# Check disk space:
df -h

# Check memory usage:
free -h

# Check system information:
uname -a
lsb_release -a  # On Ubuntu/Debian
```

#### Uninstallation of BQPhy Library

When you need to remove the BQPhy Python Library from your Linux system, follow these steps to ensure complete cleanup of all components and virtual environment.

**Step 1: Deactivate Virtual Environment**

If you currently have the BQPhy virtual environment active, deactivate it first:

```bash
# Deactivate the virtual environment
deactivate
```

Your terminal prompt should return to normal without the `(.BQP_Env)` prefix.

**Step 2: Uninstall BQPhy Package (Optional)**

Before removing the virtual environment, you can uninstall just the BQPhy package if needed:

```bash
# Activate environment first
source .BQP_Env/bin/activate

# Uninstall BQPhy package
pip uninstall bqphy -y

# Verify removal
pip list | grep -i bqphy
# Should return no results

# Deactivate environment
deactivate
```

**Step 3: Remove Virtual Environment**

Remove the entire virtual environment directory and all its contents:

```bash
# Remove virtual environment directory
rm -rf .BQP_Env

# Verify removal
if [ ! -d ".BQP_Env" ]; then
    echo "✓ Virtual environment removed successfully"
else
    echo "✗ Failed to remove virtual environment"
    ls -la .BQP_Env  # Show what's preventing removal
fi
```

**Step 4: Clean Up Project Files**

Remove any test files, example scripts, or project directories created during installation:

```bash
# Remove test files
rm -f test_bqphy.py

# Remove wheel files
rm -f *.whl
rm -f BQPhyLibrary_v*.whl

# List remaining files to verify cleanup
echo "Remaining files in current directory:"
ls -la

# Optional: Remove entire project directory
cd ..
rm -rf BQPhy_Project
echo "✓ Project directory removed"
```

**Step 5: Verification**

Verify that BQPhy has been completely removed:

```bash
# Check for remaining BQPhy files
find . -name "*bqphy*" -type f 2>/dev/null
find . -name "*BQPhy*" -type f 2>/dev/null
find . -name "*.whl" -type f 2>/dev/null

# Should return no results if completely removed
echo "If no files are listed above, BQPhy has been completely removed."
```

**Step 6: System-Wide Cleanup (Optional)**

For complete system cleanup, you may also want to:

```bash
# Clear pip cache
pip cache purge

# Clear any cached wheel files
rm -rf ~/.cache/pip/wheels/*bqphy* 2>/dev/null
rm -rf ~/.cache/pip/wheels/*BQPhy* 2>/dev/null

# Clean up user Python packages (if installed there)
rm -rf ~/.local/lib/python*/site-packages/*bqphy* 2>/dev/null
rm -rf ~/.local/lib/python*/site-packages/*BQPhy* 2>/dev/null

echo "✓ System-wide cleanup completed"
```

**Step 7: Final Verification**

Test that BQPhy is completely removed from the system:

```bash
# Test import in system Python
python3 -c "
try: 
    import bqphy
    print('⚠ BQPhy still found in system Python')
except ImportError: 
    print('✓ BQPhy successfully removed from system Python')
"

# Test import in any active virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    python -c "
try: 
    import bqphy
    print('⚠ BQPhy still found in current virtual environment')
except ImportError: 
    print('✓ BQPhy not found in current virtual environment')
"
else
    echo "ℹ No virtual environment currently active"
fi
```

**Troubleshooting Uninstallation Issues**

If you encounter problems during uninstallation:

1. **Permission Denied Errors**:
   ```bash
   # Check file permissions
   ls -la .BQP_Env
   
   # Use sudo if necessary (be careful with this)
   sudo rm -rf .BQP_Env
   
   # Fix ownership if files belong to root
   sudo chown -R $USER:$USER .
   ```

2. **Directory Not Empty Errors**:
   ```bash
   # Check what's preventing removal
   ls -la .BQP_Env/
   
   # Force removal of hidden and system files
   rm -rf .BQP_Env/.*
   rm -rf .BQP_Env
   ```

3. **Files Still in Use**:
   ```bash
   # Check for running Python processes
   ps aux | grep python
   
   # Kill any hanging Python processes (if safe to do so)
   pkill -f python
   
   # Check for open file handles
   lsof | grep -i bqphy
   ```

4. **Virtual Environment Won't Deactivate**:
   ```bash
   # Force deactivation
   unset VIRTUAL_ENV
   unset PYTHONPATH
   
   # Reload shell configuration
   source ~/.bashrc  # or ~/.zshrc depending on your shell
   ```

5. **Incomplete Removal**:
   ```bash
   # Comprehensive search for remaining files
   sudo find /home/$USER -name "*bqphy*" 2>/dev/null
   sudo find /home/$USER -name "*BQPhy*" 2>/dev/null
   
   # Check system Python directories
   python3 -c "
import sys
for path in sys.path:
    print(f'Checking: {path}')
"
   ```

**Advanced Cleanup Commands**

For thorough system cleanup:

```bash
# Remove from all user Python versions
for pyver in python3.10 python3.11 python3.12; do
    if command -v $pyver &> /dev/null; then
        echo "Checking $pyver..."
        $pyver -c "
try: 
    import bqphy
    print(f'Found BQPhy in $pyver')
except ImportError: 
    print(f'BQPhy not found in $pyver - OK')
" 2>/dev/null
    fi
done

# Clean pip configuration
rm -f ~/.pip/pip.conf

# Reset Python path
unset PYTHONPATH
unset PYTHONHOME

echo "✓ Advanced cleanup completed"
```

**Verification of Complete Removal**

Final comprehensive check:

```bash
# Create verification script
cat > verify_removal.py << 'EOF'
import sys
import os

print("=== BQPhy Removal Verification ===")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import bqphy
    print("❌ ERROR: BQPhy is still installed!")
    print(f"Location: {bqphy.__file__}")
except ImportError:
    print("✅ SUCCESS: BQPhy has been completely removed")

print(f"Current working directory: {os.getcwd()}")
print(f"VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'None')}")
print("=== Verification Complete ===")
EOF

# Run verification
python3 verify_removal.py

# Clean up verification script
rm -f verify_removal.py
```

The BQPhy library and all associated files should now be completely removed from your Linux system.


## Usage Patterns and API Design

The library supports multiple usage patterns to accommodate different levels of user expertise and optimization requirements, from simple function calls to advanced parameter configuration.

### Basic Usage Pattern

For continuous variable optimization tasks, users can invoke the optimizer with following code:

```python
import bqphy.BQPhy_Optimiser as qea

# Create and configure optimizer
optimizer = qea.BQPhy_OPTIMISER()
config = {
    "numPopulation": 100,
    "maxGeneration": 200,
    "designVariables": 5,
    "typeOfOptimisation": "CONTINUOUS",
    "lowerBounds": [-5.12] * 10,
    "upperBounds": [5.12] * 10
}
optimizer.initialize(config)
optimizer.model(objective_function)

# Run optimization
optimizer.runOptimization()  # Default: CPU execution
best_solution, best_fitness = optimizer.getBestDesign()

# Active License information viewing
qea.LicenseStatus()
```

For binary  variable optimization tasks, users can invoke the optimizer with following code:

```python
import bqphy.BQPhy_Optimiser as qea
import numpy as np

# Advanced configuration with all parameters
config = {
    "numPopulation": 200,
    "maxGeneration": 500,
    "deltaTheta": 0.05,
    "designVariables": 10,
    "typeOfOptimisation": "BINARY",
}

# Initialize with advanced parameters
optimizer = qea.BQPhy_OPTIMISER()
optimizer.initialize(config)
optimizer.model(objective_function)

# Run with GPU acceleration
optimizer.runOptimization("gpu")  # Options: "cpu", "openmp", "gpu"
best_solution, fitness_history = optimizer.getBestDesign()

# Active License information viewing
qea.LicenseStatus()
```
--- 

### Function Interface Specifications

#### Objective Function Requirements

The library requires objective functions to be vectorized for efficient population evaluation, supporting NumPy's standard array operations for optimal performance.

**Input Specification**: NumPy array of shape `(N, M)` where:
- `N`: Population size (number of candidate solutions)
- `M`: Number of design variables

**Output Specification**: NumPy array of length `N` containing fitness values

#### Objective Function Implementation Patterns

**Standard Numpy Implementation**
```python
def objective_function(x):
    """
    Vectorized objective function for BQPhy optimization
    Args:
        x: numpy array of shape (population_size, num_variables)
    Returns:
        fitness: numpy array of shape (population_size)
    """
    return np.sum(x**2, axis=1)  # Vectorized sum of squares
```

**Complex Multi-Modal Function**
```python
def rastrigin_function(x):
    """Rastrigin function - challenging multimodal test function"""
    A = 10
    fitness = np.zeros(x.shape[0], dtype=np.float64)
    for i in range(x.shape[0]):
        fitness[i] = A * x.shape[1] + np.sum(x[i]**2 - A * np.cos(2 * np.pi * x[i]))
    return fitness
```
### Constraint Handling Framework

The library supports comprehensive constraint specification and handling through penalty-based methods that integrate seamlessly with the optimization process.

#### Constraint Function Structure

The BQPhy library handles constraints through penalty functions that are integrated directly into the objective function. This approach transforms constrained optimization problems into unconstrained ones by adding penalty terms for constraint violations.

**Basic Constraint Structure**

Constraints in BQPhy follow a penalty-based approach where violations are penalized proportionally to their severity:

```python
def constrained_objective_function(x):
    """
    Template for constraint-aware objective function
    Args:
        x: numpy array of shape (population_size, num_variables)
    Returns:
        penalized_fitness: numpy array of shape (population_size,)
    """
    # 1. Calculate primary objective
    base_fitness = primary_objective(x)
    
    # 2. Evaluate constraint violations
    constraint_violations = evaluate_constraints(x)
    
    # 3. Apply penalty for violations
    penalty = penalty_coefficient * constraint_violations
    
    # 4. Return penalized fitness
    return base_fitness + penalty  # For minimization problems
```

#### Practical Constraint Examples
```python
def constrained_objective(x):
    """Objective function with constraint handling"""
    # Primary objective
    fitness = -np.sum(x**2, axis=1)  # Maximize (minimize negative)
    
    # Constraint penalties
    constraint_violation = np.maximum(0, np.sum(x, axis=1) - 5)  # Sum constraint
    penalty_factor = 1000
    
    return fitness - penalty_factor * constraint_violation
```

### Parameter Configuration

#### Core Algorithm Parameters

**Population Parameters**
- `numPopulation`: Population size for each generation (recommended: 50-200)
- `designVariables`: Number of optimization variables

**Algorithm Control Parameters**
- `deltaTheta`: Quantum rotation angle (range: 0.0-0.5, recommended: 0.05)
- `maxGeneration`: Maximum number of generations

**Optimization Type Selection**
- `typeOfOptimisation`: "BINARY" for combinatorial problems, "CONTINUOUS" for real-valued optimization

**Performance Parameters**
- Execution mode options: 'cpu' for single-threaded, 'openmp' for multi-threaded, 'gpu' for GPU acceleration

#### Convergence Criteria Configuration

The BQPhy optimizer supports flexible convergence criteria to determine when to terminate the optimization process. You can choose between generation count-based termination or fitness stagnation-based termination.

**Convergence Parameters**
- `convergenceCondition` (string): Specifies the termination criterion
  - `"generationCount"` (default): Optimization terminates after reaching `maxGeneration` generations
  - `"fitnessStagnation"`: Optimization terminates if the fitness value does not improve for a specified number of consecutive generations

- `stagnationGenerations` (integer, default: 20): Number of consecutive generations without fitness improvement needed to trigger termination. Only relevant when `convergenceCondition` is set to `"fitnessStagnation"`.

**Configuration Examples**

*Generation Count-Based Termination (Default):*
```python
config = {
    "numPopulation": 50,
    "maxGeneration": 200,
    "designVariables": 5,
    "typeOfOptimisation": "CONTINUOUS",
    
    # Convergence criteria - terminate after 200 generations
    "convergenceCondition": "generationCount",
}
```

*Fitness Stagnation-Based Termination:*
```python
config = {
    "numPopulation": 50,
    "maxGeneration": 200,
    "designVariables": 5,
    "typeOfOptimisation": "CONTINUOUS",
    
    # Convergence criteria - terminate if no improvement for 20 generations
    "convergenceCondition": "fitnessStagnation",
    "stagnationGenerations": 20,
}
```

**Behavior Summary**

| Scenario | Behavior |
|----------|----------|
| `convergenceCondition = "generationCount"` | Optimization runs exactly `maxGeneration` times or until kill signal is received |
| `convergenceCondition = "fitnessStagnation"` with `stagnationGenerations = 20` | Optimization terminates early if best fitness does not improve for 20 consecutive generations, or continues up to `maxGeneration` |
| `stagnationGenerations` not specified but `convergenceCondition = "fitnessStagnation"` | Uses default value of 20 generations |

**Best Practices**

1. **Use `"generationCount"`** when you want consistent runtime or need a fixed number of evaluations for comparison studies
2. **Use `"fitnessStagnation"`** to save computation time by terminating when the algorithm has converged
3. **Adjust `stagnationGenerations`** based on problem characteristics:
   - Use smaller values (5-10) for small problems where plateaus are clear
   - Use larger values (30-50) for complex problems with noisy fitness landscapes
4. Always set `maxGeneration` as a safety limit even when using `"fitnessStagnation"` to prevent indefinite runs

#### Initial Population Seeding Configuration

The BQPhy library supports user-defined initial population seeding, allowing you to guide the optimization process by providing starting chromosomes from prior knowledge, previous optimization runs, or engineered solutions.

**Seeding Parameters**
- `populationInitialSeeding` (boolean, default: False): Set to `True` to enable initialization from a CSV file, `False` to use random initialization
- `populationInitCSVFilePath` (string): Path to the CSV file containing initial population data

**CSV File Format**

The CSV file for initial population seeding must follow a specific format:

- **Structure**: One chromosome per row
- **Columns**: Each column represents one design variable (must equal `designVariables` in config)
- **Values**: 
  - For BINARY optimization: 0 or 1 (representing binary choices)
  - For CONTINUOUS optimization: Floating-point values within the specified bounds (between `lowerBounds` and `upperBounds`)
- **Separators**: Values must be comma-separated
- **Encoding**: For CONTINUOUS problems, continuous values are internally encoded into binary representation
**Example CSV File (for problem with 5 design variables):**

```csv
1,0.5,2.3,1.0,0.8
0,1.2,3.1,0.5,1.5
1,0.7,2.8,1.2,0.9
1,0.3,3.5,0.8,1.1
```

**Behavior Summary**

| Scenario | Behavior |
|----------|----------|
| CSV has `n` rows where `n < numPopulation` | First `n` chromosomes initialized from CSV; remaining `numPopulation - n` chromosomes randomly initialized |
| CSV has `n` rows where `n = numPopulation` | All chromosomes initialized from CSV |
| CSV has `n` rows where `n > numPopulation` | First `numPopulation` rows from CSV are used; excess rows beyond `numPopulation` are discarded |
| `populationInitialSeeding = False` | Entire population randomly initialized (CSV file ignored even if path provided) |

**Configuration Example**

```python
config = {
    "numPopulation": 50,
    "maxGeneration": 200,
    "designVariables": 5,
    "typeOfOptimisation": "CONTINUOUS",
    "lowerBounds": [-5.0, -3.0, 0.0, -2.0, -1.0],
    "upperBounds": [5.0, 3.0, 10.0, 2.0, 1.0],
    
    # Initial population seeding configuration
    "populationInitialSeeding": True,
    "populationInitCSVFilePath": "path/to/initial_population.csv",
}

optimizer = qea.BQPhy_OPTIMISER()
optimizer.initialize(config)
optimizer.model(objective_function)
optimizer.runOptimization()
```

**Best Practices for Initial Population Seeding**

1. **Warm-starting from Prior Knowledge**: Use solutions from domain expertise or previous optimization runs to accelerate convergence
2. **Multi-Start Strategy**: Initialize population with diverse good solutions to explore different regions of the search space
3. **Constraint-Aware Seeding**: For constrained problems, ensure initial solutions satisfy constraints to guide the optimizer toward feasible regions
4. **Validation**: Always verify CSV file format before running optimization to avoid parsing errors
5. **Variable Ordering**: Ensure CSV columns match the order of design variables in your problem definition

#### Variable Bounds Specification

For continuous optimization problems, variable bounds are specified using Python lists:

```python
# Simple bounds for all variables
lowerBounds = [-5.0] * num_variables  # Lower bounds
upperBounds = [5.0] * num_variables   # Upper bounds

# Variable-specific bounds
config = {
    "lowerBounds": [-10, -5, 0],    # Different lower bound per variable
    "upperBounds": [10, 5, 1]      # Different upper bound per variable
}
```

#### Optimization Control and Termination (Kill Switch)

The BQPhy optimizer supports graceful termination through an automatic kill switch mechanism, allowing users to stop optimization runs at any time without losing intermediate results.

**Kill Switch Mechanism**

The kill switch works through a simple file-based control:

- **Automatic File Creation**: The `kill_switch.txt` file is created automatically in the current working directory when optimization starts
- **Default State**: File is initialized with `kill:0` (continue optimization)
- **Graceful Shutdown**: When the optimizer detects `kill:1` during a generation, it:
  1. Completes the current generation processing
  2. Saves all restart files and intermediate results
  3. Logs the termination event
  4. Returns the best solution found so far

**How to Use Kill Switch**

The usage is simple - just edit the control flag:

```
# kill_switch.txt (auto-created during optimization)
# Control file
# Set kill:1 to stop simulation
kill:0    # While running - optimization continues
kill:1    # Edit this to stop optimization gracefully
```

**Method 1: Using Text Editor (Recommended)**

While your optimization is running:

```bash
# Terminal 1: Run your optimization script
python optimize_my_problem.py

# Terminal 2: Edit the file to trigger shutdown
# Open kill_switch.txt in your editor and change:
#   kill:0  →  kill:1
```

**Method 2: Using Command Line**

```bash
# Replace kill:0 with kill:1 to trigger shutdown
sed -i 's/kill:0/kill:1/g' kill_switch.txt

# Or using echo (overwrites the file)
echo "kill:1" > kill_switch.txt
```

**Method 3: Using Python**

```python
# Trigger kill switch from another terminal or script
with open('kill_switch.txt', 'w') as f:
    f.write('kill:1')

print("Kill switch activated!")
```

**Monitoring Output**

When kill switch is detected, you'll see output like:

```
[Watcher] Kill signal detected! Stopping simulation...
[Solver] Writing restart files...
[Solver] Restart write complete.
```

**Important Considerations**

1. **Automatic File Creation**: The `kill_switch.txt` file is created automatically in the current working directory during optimization - no manual creation needed
2. **Timing**: Kill switch is checked at the beginning of each generation, so there may be a slight delay before termination
3. **File State**: The file persists after termination. Before the next run, ensure it's reset to `kill:0` or create a fresh run
4. **Recovery**: The optimizer saves intermediate results, allowing you to analyze the best solution found before termination

**Resetting for Next Run**

```bash
# Reset kill switch for next optimization run
echo "kill:0" > kill_switch.txt

# Or verify the current state
cat kill_switch.txt
```

#### Restart and Recovery Features

The BQPhy Python library provides comprehensive restart and recovery capabilities, allowing you to save optimization checkpoints and resume from previous runs. This is particularly useful for long-running optimizations, exploratory tuning, and fault tolerance.

**Overview**

The library supports two complementary restart mechanisms:
- **Restart Dump**: Periodically saves population state during optimization (checkpointing)
- **Restart Solver**: Recovers from saved checkpoints to continue optimization

##### Restart Dump Configuration

**Dump Parameters**
- `restartDump` (boolean, default: False): Enable periodic saving of population state
- `restartDumpFrequency` (integer, default: 50): Save checkpoint every N generations
- `restartDumpPath` (string, default: "restart/data.txt"): Directory and file pattern for checkpoint files

**How Restart Dump Works**

When enabled, restart dump:
1. Saves complete population state (theta values and chromosome data) every `restartDumpFrequency` generations
2. Creates timestamped checkpoint files with the format: `basename_NNNN.txt` where NNNN is the generation number
3. Automatically creates the specified directory if it doesn't exist
4. Overwrites older checkpoints to manage disk space (retains only recent dumps)

**Configuration Example**

```python
import sys
sys.path.append('path/to/bqphy')
import bqphy as qea

# Define objective function (Rastrigin)
def objective_function(x):
    return 10 * x.shape[1] + np.sum(x**2 - 10 * np.cos(2 * np.pi * x), axis=1)

# Initialize configuration with restart dump enabled
config = {
    "numPopulation": 200,
    "maxGeneration": 200,
    "deltaTheta": 0.05,
    "designVariables": 4,
    "typeOfOptimisation": "CONTINUOUS",
    "lowerBounds": [-5.0] * 4,
    "upperBounds": [5.0] * 4,
    
    # Enable restart dump configuration
    "restartDump": True,
    "restartDumpFrequency": 30,          # Save every 30 generations
    "restartDumpPath": "Myrestart/restart_data.txt",
}

# Initialize and run optimizer
optimizer = qea.BQPhy_OPTIMISER()
optimizer.initialize(config)
optimizer.model(objective_function)
optimizer.runOptimization()

best_solution, fitness_history = optimizer.getBestDesign()
```

**Output Structure**

When `restartDumpPath = "Myrestart/restart_data.txt"` is specified:

```plaintext
Myrestart/
├── restart_data_0030.txt    # Checkpoint from generation 30
├── restart_data_0060.txt    # Checkpoint from generation 60
├── restart_data_0090.txt    # Checkpoint from generation 90
├── restart_data_0120.txt    # Checkpoint from generation 120
└── restart_data_0150.txt    # Checkpoint from generation 150
```

Each checkpoint file contains:
- Population size and optimization type
- Theta values (quantum rotation angles for each chromosome)
- Population bitstring representations (if applicable)

**Best Practices for Restart Dump**

1. **Frequency Selection**: Choose `restartDumpFrequency` based on:
   - Longer intervals (50-100 generations) for computationally cheap fitness functions
   - Shorter intervals (10-30 generations) for expensive fitness functions
   - Consider disk I/O overhead vs. checkpoint coverage

2. **Disk Space Management**: 
   - Monitor checkpoint file sizes, especially for large populations
   - Each checkpoint is typically proportional to `numPopulation × designVariables`
   - Use separate directories for different optimization runs

3. **Path Configuration**:
   - Use absolute paths for multi-run setups to avoid confusion
   - Ensure write permissions to the specified directory
   - Create directories beforehand or let the optimizer create them

##### Restart Solver Configuration

**Resume Parameters**
- `natureOfRun` (string, default: "newRun"): Specifies whether to start fresh or resume
  - **`"newRun"`**: Start a fresh optimization from random initialization (ignore restart files)
  - **`"restartSolver"`**: Resume from the latest checkpoint file
  
- `restartReadPath` (string): Path pattern for reading checkpoint files
  - Use `*` as wildcard to automatically find the latest checkpoint file
  - Example: `"Myrestart/restart_data_*.txt"` will find and load the most recent file

**How Restart Solver Works**

When `natureOfRun = "restartSolver"`:
1. Searches for checkpoint files matching the pattern in `restartReadPath`
2. Automatically identifies the latest checkpoint (highest generation number)
3. Loads the complete population state from that checkpoint
4. Resumes optimization from the next generation
5. All subsequent generations continue with the same configuration

**Configuration Example: Fresh Run**

```python
config = {
    "numPopulation": 200,
    "maxGeneration": 200,
    "deltaTheta": 0.05,
    "designVariables": 4,
    "typeOfOptimisation": "CONTINUOUS",
    "lowerBounds": [-5.0] * 4,
    "upperBounds": [5.0] * 4,
    
    # Fresh run configuration (default behavior)
    "natureOfRun": "newRun",
}

# Initialize and run optimizer
optimizer = qea.BQPhy_OPTIMISER()
optimizer.initialize(config)
optimizer.model(objective_function)
optimizer.runOptimization()

best_solution, fitness_history = optimizer.getBestDesign()
```

**Configuration Example: Restart from Checkpoint**

```python
config = {
    "numPopulation": 200,
    "maxGeneration": 400,               # Run for additional 200 generations
    "deltaTheta": 0.05,
    "designVariables": 4,
    "typeOfOptimisation": "CONTINUOUS",
    "lowerBounds": [-5.0] * 4,
    "upperBounds": [5.0] * 4,
    
    # Restart configuration - resume from saved checkpoint
    "natureOfRun": "restartSolver",
    "restartReadPath": "Myrestart/restart_data_*.txt",  # Wildcard finds latest
}

# Initialize and run optimizer
optimizer = qea.BQPhy_OPTIMISER()
optimizer.initialize(config)
optimizer.model(objective_function)
optimizer.runOptimization()

best_solution, fitness_history = optimizer.getBestDesign()
```

**Behavior Summary**

| Scenario | Behavior |
|----------|----------|
| `natureOfRun = "newRun"` | Always starts fresh from random initialization (restartReadPath ignored) |
| `natureOfRun = "restartSolver"`, wildcard in path | Finds latest checkpoint file automatically and resumes from it |
| `natureOfRun = "restartSolver"`, specific file path | Resumes from the specified checkpoint file |
| `natureOfRun = "restartSolver"`, no matching file found | Raises an exception; ensure checkpoint files exist and path is correct |

**Advanced Workflow: Checkpoint and Resume**

```python
import numpy as np

# Phase 1: Initial optimization run with checkpointing
config1 = {
    "numPopulation": 200,
    "maxGeneration": 100,
    "deltaTheta": 0.05,
    "designVariables": 4,
    "typeOfOptimisation": "CONTINUOUS",
    "lowerBounds": [-5.0] * 4,
    "upperBounds": [5.0] * 4,
    "restartDump": True,
    "restartDumpFrequency": 20,
    "restartDumpPath": "checkpoints/run1.txt",
    "natureOfRun": "newRun",
}

optimizer1 = qea.BQPhy_OPTIMISER()
optimizer1.initialize(config1)
optimizer1.model(objective_function)
optimizer1.runOptimization()

X1, fitness1 = optimizer1.getBestDesign()
print(f"Phase 1 - Best fitness after 100 generations: {fitness1[-1]:.6f}")

# Phase 2: Resume optimization from latest checkpoint for additional generations
config2 = {
    "numPopulation": 200,
    "maxGeneration": 200,               # Total of 200 generations
    "deltaTheta": 0.05,
    "designVariables": 4,
    "typeOfOptimisation": "CONTINUOUS",
    "lowerBounds": [-5.0] * 4,
    "upperBounds": [5.0] * 4,
    "restartDump": True,
    "restartDumpFrequency": 20,
    "restartDumpPath": "checkpoints/run1.txt",
    "natureOfRun": "restartSolver",
    "restartReadPath": "checkpoints/run1_*.txt",
}

optimizer2 = qea.BQPhy_OPTIMISER()
optimizer2.initialize(config2)
optimizer2.model(objective_function)
optimizer2.runOptimization()

X2, fitness2 = optimizer2.getBestDesign()
print(f"Phase 2 - Best fitness after 200 total generations: {fitness2[-1]:.6f}")

# Compare results
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(fitness1, label='Phase 1 (0-100 gen)', marker='o')
plt.plot(range(len(fitness1)-1, len(fitness2)), fitness2[len(fitness1)-1:], 
         label='Phase 2 (100-200 gen)', marker='s')
plt.xlabel('Generation')
plt.ylabel('Best Fitness')
plt.title('Multi-phase Optimization with Restart')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(range(len(fitness2)), fitness2, label='Combined History', marker='^')
plt.xlabel('Generation')
plt.ylabel('Best Fitness')
plt.title('Combined Optimization Trajectory')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
```

**Best Practices for Restart Features**

1. **Combined Dump and Resume**: Always enable `restartDump` before running long optimizations so you have checkpoints available for recovery
2. **Separate Checkpoint Directories**: Use different directories for different optimization problems or runs to avoid confusion
3. **Generation Limit**: When resuming, set `maxGeneration` to a value greater than the checkpoint generation to continue optimization
4. **Error Handling**: Always verify checkpoint files exist before resuming, especially in automated workflows
   ```python
   import os
   import glob
   
   # Verify checkpoint files exist before resuming
   checkpoint_pattern = "checkpoints/run1_*.txt"
   checkpoints = glob.glob(checkpoint_pattern)
   
   if not checkpoints:
       raise FileNotFoundError(f"No checkpoint files found matching {checkpoint_pattern}")
   
   latest_checkpoint = sorted(checkpoints)[-1]
   print(f"Resuming from: {latest_checkpoint}")
   ```
5. **Path Consistency**: Keep `restartDumpPath` and `restartReadPath` consistent across runs for the same problem
6. **Monitoring**: Use generation logging (`generationLogging` parameter) with restart to track continuous progress across sessions

#### Logging and Output Configuration

The BQPhy Python library provides flexible output and logging capabilities for monitoring optimization progress and saving results.

**Output Directory Configuration**
- `outputFilePath` (optional, string): Specifies the directory where all output files will be saved. If not provided, a default timestamped directory (`Run_YYYY-MM-DD-HH-MM-SS`) is created in the current working directory.
  
  ```python
  config = {
      "outputFilePath": "./results/optimization_run_1",
      # ... other parameters
  }
  ```

**Generation Logging Mode**
- `generationLogging` (optional, string): Controls the level of detail in generation-by-generation logging. Three modes are available:
  
  - **`"noLogging"`** (default): No generation log files are created. Only CSV summary files are generated if `writeCSV()` is called.
  
  - **`"minimumLogging"`**: Creates a timestamped CSV log file with essential generation statistics:
    - Trial Number
    - Generation ID
    - Overall Fitness (best fitness of current generation)
    - Minimum Fitness (best in population)
    - Maximum Fitness (worst in population)
    - Generation Elapsed Time (in milliseconds)
  
  - **`"verboseLogging"`**: Creates a detailed CSV log file with all fields from `minimumLogging` plus:
    - Fitness Vector: Complete fitness values of entire population for each generation

**File Organization**

When executing with logging enabled, files are organized as follows:

```plaintext
outputFilePath/
├── BQPhy_generations_log_YYYY-MM-DD_HH-MM-SS.csv    (generation log - if logging enabled)
└── results/
    ├── output_DesignVariable_model.csv               (design variables across trials)
    └── output_GenidVSFitness_model.csv               (fitness convergence across trials)
```

**Complete Configuration Example**

```python
config = {
    "numPopulation": 100,
    "maxGeneration": 200,
    "deltaTheta": 0.05,
    "designVariables": 5,
    "typeOfOptimisation": "CONTINUOUS",
    "lowerBounds": [-5.0] * 5,
    "upperBounds": [5.0] * 5,
    
    # Output configuration
    "outputFilePath": "./optimization_results",      # Custom output directory
    "generationLogging": "verboseLogging",           # Enable detailed logging
}

# Initialize and run optimizer
optimizer = BQPhy_OPTIMISER()
optimizer.initialize(config)
optimizer.model(objective_function)
optimizer.runOptimization()

# Optionally save final CSV results (appends to existing files)
# Note: writeCSV is optional and uses the same outputFilePath
optimizer.writeCSV()
```

**Behavior Summary**

| Scenario | Behavior |
|----------|----------|
| No `outputFilePath`, no `generationLogging` | Default timestamped directory created; no logs |
| `outputFilePath` specified, `generationLogging = "noLogging"` | Outputs saved to outputFilePath; no logs |
| `outputFilePath` specified, `generationLogging = "minimumLogging"` | Log files in outputFilePath; CSV files in outputFilePath/results |
| `outputFilePath` specified, `generationLogging = "verboseLogging"` | Detailed logs in outputFilePath; CSV files in outputFilePath/results |

---

## Performance Optimization Guidelines

### Vectorization Best Practices

**Inefficient Implementation (Avoid)**
```python
def inefficient_objective(x):
    fitness = []
    for i in range(x.shape[0]):
        f = 0
        for j in range(x.shape[1]):
            f += x[i,j]**2
        fitness.append(f)
    return np.array(fitness)
```

**Efficient Implementation (Recommended)**
```python
def efficient_objective(x):
    return np.sum(x**2, axis=1)  # Vectorized numpy operations
```

### Memory Management

For large-scale optimization problems, consider memory-efficient implementations:

```python
def memory_efficient_objective(x):
    """Process in chunks for large populations"""
    chunk_size = 1000
    n_samples = x.shape[0]
    fitness = np.zeros(n_samples)
    
    for i in range(0, n_samples, chunk_size):
        end_idx = min(i + chunk_size, n_samples)
        chunk = x[i:end_idx]
        fitness[i:end_idx] = compute_chunk(chunk)
    
    return fitness
```

## Output Interpretation

### Standard Output Structure

The optimization method returns two primary outputs:

**Optimal Solution** (`best_solution`): Best design variables found during optimization  
**Fitness History** (`best_fitness`): Fitness evolution across generations

### Results Analysis

```python
# Run optimization
optimizer.runOptimization()
best_solution, fitness_history = optimizer.getBestDesign()

# Analyze results
print(f"Optimal solution: {best_solution}")
print(f"Best fitness: {fitness_history[-1]:.6f}")

# Plot convergence
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.plot(fitness_history)
plt.xlabel('Generation')
plt.ylabel('Best Fitness')
plt.title('Optimization Convergence')
plt.grid(True)
plt.show()
```

## Environment Configuration

### Creating Virtual Environment

**Virtual environments are crucial** when installing wheel packages like BQPhy. Here's why:

- **Dependency Isolation**: Prevents conflicts between different Python projects and their dependencies
- **System Protection**: Keeps your system Python installation clean and stable
- **Reproducible Environments**: Ensures consistent behavior across different machines and deployments
- **Easy Cleanup**: Simple to remove entire project environment if no longer needed

#### Linux Virtual Environment Setup

Navigate to your project directory before creating the environment.

1. **Create the virtual environment:**
   ```bash
   python3.12 -m venv .BQP_Env
   ```

2. **Activate the virtual environment:**
   ```bash
   source .BQP_Env/bin/activate
   ```
   Your terminal prompt should now show `(.BQP_Env)` at the beginning.

3. **Verify activation (optional):**
   ```bash
   pip list
   ```
   This will show only the basic packages installed in your new environment.

#### Windows Virtual Environment Setup

1. **Open Command Prompt or PowerShell:**
   - Press `Win + R`, type `cmd` or `powershell`, and press Enter
   - Or search for "Command Prompt" or "PowerShell" in the Start menu

2. **Navigate to your project directory:**
   ```cmd
   cd C:\path\to\your\project
   ```

3. **Create the virtual environment:**
   ```cmd
   python -m venv .BQP_Env
   ```
   *Note: Use `python3.12` if you have multiple Python versions installed*

4. **Activate the virtual environment:**
   
   **For Command Prompt (cmd):**
   ```cmd
   .BQP_Env\Scripts\activate.bat
   ```
   
   **For PowerShell:**
   ```powershell
   .BQP_Env\Scripts\Activate.ps1
   ```
   
   *If you get an execution policy error in PowerShell, run:*
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

5. **Verify the environment (optional):**
   ```cmd
   pip list
   ```

6. **Your prompt should change to show the virtual environment:**
   ```
   (.BQP_Env) C:\path\to\your\project>
   ```

## Usage Examples

### Continuous Optimization Example

The following comprehensive example demonstrates the BQPhy library's capabilities for solving continuous optimization problems using the challenging Rastrigin function.

#### Sample 1: Rastrigin Function

- **Problem**: Rastrigin function minimization  
- **Type**: Multi-modal continuous optimization
- **Difficulty**: Advanced
- **Features**: Highly multi-modal with many local optima
- **Usage**: `python3 continuous_rastrigin.py`

**About Rastrigin Function**

The Rastrigin function is a highly multi-modal function with many local optima, making it a challenging test case for optimization algorithms.

The mathematical formulation of the Rastrigin function is:

$$
f(x) = A \cdot n + \sum_{i=1}^{n} \left[ x_i^2 - A \cdot \cos(2\pi x_i) \right]
$$

Where:
- $A = 10$ (constant parameter)
- $n$ is the number of dimensions
- $x_i$ are the input variables
- Global minimum: $f(0, 0, ..., 0) = 0$
- Search domain: $x_i \in [-5.12, 5.12]$ for all $i$

**Step 1: Import Libraries**
```python
import numpy as np
import bqphy.BQPhy_Optimiser as qea
```

**Step 2: Define the Rastrigin Model**
```python
def rastrigin_function(x):
    A = 10
    fitness = np.zeros(x.shape[0], dtype=np.float64)
    for i in range(x.shape[0]):
        fitness[i] = (A * x.shape[1] + np.sum(x[i]**2 - A * np.cos(2 * np.pi * x[i])))
    return fitness
```

**Step 3: Call the model from the main function**

```python
def main():
    print("BQPhy Continuous Optimization Example")
    print("Problem: Rastrigin Function Minimization")
    print("=" * 60)
    
    # Problem configuration
    config = {
        "numPopulation": 100,
        "maxGeneration": 200,
        "deltaTheta": .05,
        "designVariables": 5,
        "typeOfOptimisation": "CONTINUOUS",
        "lowerBounds": [-5.12] * 5,
        "upperBounds": [5.12] * 5,
    }
        
    # Initialize optimizer
    print("Initializing BQPhy optimizer...")
    optimizer = qea.BQPhy_OPTIMISER()
    optimizer.initialize(config)
    optimizer.model(rastrigin_function)
    
    # Run optimization
    print("⚡ Running optimization...")
    optimizer.runOptimization()     # "cpu" can also be specified for serial execution # "openmp" for parallel execution # "gpu" for GPU execution

    # Get best solution
    best_solution, best_fitness = optimizer.getBestDesign()
    
    # Display results
    print("\n" + "=" * 60)
    print("Optimization Complete!")
    print(f"Best Solution: {[f'{x:.6f}' for x in best_solution]}")
    print(f"Best Fitness: {best_fitness[-1]:.8f}")
    print(f"Expected: All zeros with fitness ≈ 0.0")
    print(f"Quality: {'Excellent' if best_fitness[-1] < 1e-3 else 'Good' if best_fitness[-1] < 1.0 else 'Fair'}")
    
if __name__ == "__main__":
    main()
```

### Binary Optimization Example

#### Sample 2: 0/1 Knapsack Problem

- **Problem**: 0-1 Knapsack problem
- **Type**: Combinatorial optimization
- **Difficulty**: ⭐⭐ Intermediate
- **Features**: Classic discrete optimization with constraints
- **Usage**: `python3 binary_knapsack.py`

**About 0/1 Knapsack Problem**

The knapsack problem: given a set of items with weights and values, select items to maximize value while staying within weight capacity.

The mathematical formulation of the 0/1 Knapsack problem is:

**Objective Function:**
$$
\text{Maximize: } \sum_{i=1}^{n} v_i \cdot x_i
$$

**Subject to constraints:**
$$
\sum_{i=1}^{n} w_i \cdot x_i \leq W
$$

$$
x_i \in \{0, 1\} \quad \forall i = 1, 2, ..., n
$$

Where:
- $n$ is the number of items
- $v_i$ is the value of item $i$
- $w_i$ is the weight of item $i$
- $W$ is the maximum weight capacity of the knapsack
- $x_i$ is the decision variable: 1 if item $i$ is selected, 0 otherwise

**Step 1: Import Libraries**
```python
import numpy as np
import bqphy.BQPhy_Optimiser as qea
```

**Step 2: Define the Knapsack Model**

```python 
# Problem data - small knapsack instance
ITEMS = [
    {"value": 60, "weight": 10},   # Item 0
    {"value": 100, "weight": 20},  # Item 1
    {"value": 120, "weight": 30},  # Item 2
    {"value": 80, "weight": 15},   # Item 3
    {"value": 90, "weight": 25},   # Item 4
    {"value": 150, "weight": 35},  # Item 5
    {"value": 70, "weight": 12},   # Item 6
    {"value": 110, "weight": 28},  # Item 7
]
CAPACITY = 50

def knapsack_fitness(x):   
    Weights = np.array([item["weight"] for item in ITEMS])
    Values = np.array([item["value"] for item in ITEMS])

    # If x is a 1D vector of selection variables:
    total_weights = x @ Weights
    total_values = x @ Values

    # Fitness: negative value (since you're minimizing) + penalty
    fitness = -total_values
    penalty = np.maximum(total_weights - CAPACITY, 0)
    penaltyCoeff = 1000
    fitness += penalty * penaltyCoeff  # Large penalty for exceeding capacity

    return fitness
```

**Step 3: Call the model from the main function**
```python
def main():   
    # Display problem instance
    print("Available Items:")
    for i, item in enumerate(ITEMS):
        ratio = item["value"] / item["weight"]
        print(f"   Item {i}: Value={item['value']:3d}, Weight={item['weight']:2d}, Ratio={ratio:.1f}")
    print(f"\n Knapsack Capacity: {CAPACITY}")
    print()
    
    # Problem configuration
    config = {
        "numPopulation": 100,
        "maxGeneration": 200,
        "deltaTheta": .05,
        "designVariables": len(ITEMS),
        "typeOfOptimisation": "BINARY"
    }
    
    # Initialize optimizer
    print("🔄 Initializing BQPhy optimizer...")
    optimizer = qea.BQPhy_OPTIMISER()
    optimizer.initialize(config)
    optimizer.model(knapsack_fitness)
    
    # Run optimization
    print("⚡ Running optimization...")
    optimizer.runOptimization()     

    # Get best solution
    best_solution, best_fitness = optimizer.getBestDesign()
   
    # Calculate solution details
    total_weight = sum(best_solution[i] * ITEMS[i]["weight"] for i in range(len(ITEMS)))
    total_value = sum(best_solution[i] * ITEMS[i]["value"] for i in range(len(ITEMS)))
   
    # Display results
    print("\n" + "=" * 60)
    print("✅ Optimization Complete!")
    print(f"🎯 Best Solution: {best_solution}")
    print(f"📈 Best Fitness: {best_fitness}")
    print(f"💰 Total Value: {total_value}")
    print(f"⚖️ Total Weight: {total_weight}/{CAPACITY}")
    
    # Check if solution is feasible
    feasible = total_weight <= CAPACITY
    print(f"\n🏆 Solution Status: {'✅ Feasible' if feasible else '❌ Infeasible'}")
    
    # Calculate efficiency
    if feasible:
        efficiency = total_value / CAPACITY  # value per unit capacity
        print(f"💡 Efficiency: {efficiency:.2f} value per unit capacity")

if __name__ == "__main__":
    main()
```
---

## Conclusion

The BQPhy Python Library represents a powerful and comprehensive optimization solution that successfully bridges the gap between advanced quantum-inspired algorithms and practical engineering applications within the Python scientific computing environment. This user guide has provided detailed coverage of all essential aspects required for effective utilization of the library, from basic installation procedures to advanced optimization techniques and real-world application examples.

### Documentation Coverage Summary

This guide has systematically covered all critical aspects of BQPhy library usage:

- **Installation and Configuration**: Comprehensive procedures for Python 3.12 installation, virtual environment setup, and library installation across multiple operating systems
- **Architecture Understanding**: Detailed explanation of the library's structure, component organization, and pybind11 integration patterns
- **Programming Interface**: Complete specification of function interfaces, parameter configuration, and optimization workflows
- **Performance Guidelines**: Best practices for vectorization, memory management, and computational efficiency in Python
- **Practical Examples**: Real-world demonstrations through continuous Rastrigin function and binary knapsack optimization problems
- **Advanced Features**: Parameter tuning strategies, results analysis techniques, and visualization approaches using Python scientific stack

### Best Practices for Success

**Start Simple**: Begin with the provided examples to understand basic usage patterns before tackling complex optimization problems. The continuous and binary examples serve as excellent templates for developing custom applications.

**Leverage Vectorization**: Always implement objective functions using NumPy's vectorized operations to achieve optimal performance with population-based algorithms.

**Parameter Tuning**: Experiment with algorithm parameters, particularly population size, generation limits, and quantum rotation angles, to achieve optimal performance for specific problem domains.

**Environment Management**: Always use virtual environments to maintain clean installations and avoid dependency conflicts with other Python projects.

**Results Validation**: Always verify optimization results through comprehensive analysis including constraint satisfaction, convergence behavior, and solution quality assessment.

### Final Considerations

The BQPhy Python Library provides a robust foundation for addressing complex optimization challenges within Python's rich scientific computing ecosystem. By combining quantum-inspired algorithmic innovation with Python's ease of use and extensive library support, the toolkit enables users to tackle previously intractable problems while maintaining development efficiency and code maintainability.

Success with the BQPhy library depends not only on understanding its technical capabilities but also on applying sound optimization methodology including proper problem formulation, objective function design, and results validation. This documentation provides the comprehensive foundation necessary for achieving both immediate optimization goals and long-term development success.

The quantum-inspired optimization paradigm represents an exciting frontier in computational optimization, and the BQPhy Python Library provides an accessible and powerful platform for exploring and applying these advanced techniques to real-world engineering, scientific, and business challenges.


## Getting Help

If you encounter issues not covered here, please contact BQP Support for assistance
---
*For technical support, additional documentation, or licensing inquiries, please contact the BQPhy development team through the appropriate channels specified in your license agreement.*

*Last updated: March 2026*