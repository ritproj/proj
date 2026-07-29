<!--
    Document: BQPhy System Compatibility Guide
    Creator: HPC Team
    Date: January 31, 2026
    Version: Preview 1.0
    Description: Comprehensive system compatibility guide covering common requirements, compatibility checks, and troubleshooting procedures for both BQPhy MATLAB Toolkit and Python Library deployments across Linux and Windows platforms. Includes GLIBC management, architecture verification, and platform-specific diagnostic tools.
-->
# BQPhy System Compatibility Guide

This guide addresses common system requirements and compatibility issues that apply to both **BQPhy MATLAB Toolkit** and **BQPhy Python Library** deployments.

## System Requirements

Both BQPhy MATLAB Toolkit and Python Library share the following core system requirements:

### Operating System Support
- **Linux**: Ubuntu 20.04+, CentOS Stream 9+, RHEL 9+, Fedora 35+, Debian 11+
- **Windows**: Windows 10/11 (64-bit)
- **Architecture**: x86_64 (64-bit) required for both platforms

### Linux-Specific Requirements
- **GLIBC Version**: 2.32 or higher (critical for both MATLAB and Python deployments)
- **Memory**: Minimum 2GB RAM (4GB+ recommended for large-scale optimizations)
- **Disk Space**: At least 200MB free space

### Windows-Specific Requirements
- **Visual C++ Runtime**: Microsoft Visual C++ Redistributable 2019 or later
- **Memory**: Minimum 2GB RAM (4GB+ recommended)
- **Disk Space**: At least 200MB free space

## Compatibility Verification

### Universal System Checks

Check your system compatibility before installing either BQPhy toolkit:

```bash
# Linux Systems
# Check GLIBC version (should be 2.32+)
ldd --version | head -1
# Expected: ldd (GNU libc) 2.32 or higher

# Check architecture (should show x86_64)
uname -m
# Expected: x86_64

# Check available memory
free -h

# Check disk space
df -h
```

```powershell
# Windows Systems (PowerShell)
# Check system architecture
[System.Environment]::Is64BitProcess
# Expected: True

# Check Windows version
Get-ComputerInfo | Select WindowsProductName, WindowsVersion

# Check available memory
Get-ComputerInfo | Select TotalPhysicalMemory

# Check disk space
Get-PSDrive -PSProvider FileSystem
```

### Platform-Specific Checks

**For Python Library Deployment:**
```bash
# Check Python version (must be 3.10.x or 3.12.x)
python3 --version
# or
python --version

# Verify pip version
pip --version
```

**For MATLAB Toolkit Deployment:**
```matlab
% Check MATLAB version (R2020b or later recommended)
version

% Check MATLAB architecture
computer('arch')
% Expected: 'win64' or 'glnxa64'

% Check available toolboxes
ver
```

## GLIBC Version Management (Linux)

GLIBC compatibility is critical for both BQPhy deployments on Linux systems.

### GLIBC Version Check

To verify your GLIBC version meets requirements:

```bash
# Method 1: Using ldd
ldd --version | head -1

# Method 2: Using getconf
getconf GNU_LIBC_VERSION

# Method 3: Check system library directly
/lib/x86_64-linux-gnu/libc.so.6
```

Expected output should show version 2.32 or higher:
```
ldd (GNU libc) 2.35
```

### GLIBC Upgrade Options

⚠️ **Warning**: Upgrading GLIBC can be risky and may break your system. Consider these safer alternatives:

**Option 1: Distribution Upgrade (Recommended)**
```bash
# For Ubuntu/Debian
sudo apt update && sudo apt upgrade
sudo do-release-upgrade

# For RHEL/CentOS
sudo dnf update
sudo dnf system-upgrade

# For Fedora
sudo dnf update
sudo dnf system-upgrade download --releasever=<newer_version>
```

**Option 2: Docker Containerization**

If your host system cannot be upgraded, use Docker for consistent environments:

```dockerfile
# Universal BQPhy Container Base
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    curl \
    wget

# For Python Library support
RUN apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3.12-pip \
    python3.12-dev

# For MATLAB integration (if needed)
# Add MATLAB Runtime installation steps here

WORKDIR /app
```

## Common Compatibility Issues

### Issue 1: GLIBC Version Mismatch

**Symptoms:**
- `ImportError: /lib64/libc.so.6: version 'GLIBC_2.32' not found` (Python)
- Library loading errors in MATLAB

**Solutions:**
1. Upgrade Linux distribution (recommended)
2. Use Docker containerization
3. Contact BQP support for older system compatibility

### Issue 2: Architecture Incompatibility

**Symptoms:**
- "Architecture not supported" errors
- Library fails to load on ARM systems

**Solutions:**
- Ensure x86_64 system architecture
- ARM64/AArch64 support requires special builds (contact BQP support)

### Issue 3: Python Version Conflicts (Python Library)

**Symptoms:**
- "Python version not supported" during installation
- Import failures after installation

**Solutions:**
- Use exactly Python 3.10 or 3.12
- Use virtual environments to isolate Python versions
- Install correct Python version using package manager

### Issue 4: MATLAB Version Incompatibility (MATLAB Toolkit)

**Symptoms:**
- MEX compilation failures
- Toolkit installation errors

**Solutions:**
- Use MATLAB R2020b or later
- Ensure MATLAB Compiler Runtime compatibility
- Verify MATLAB architecture matches system (64-bit)

## Support and Troubleshooting

### Diagnostic Information Collection

Before contacting support, collect this system information:

```bash
# Linux Diagnostic Script
echo "=== System Information ==="
uname -a
echo "=== GLIBC Version ==="
ldd --version | head -1
echo "=== Python Version ==="
python3 --version 2>/dev/null || echo "Python not found"
echo "=== MATLAB ==="
which matlab 2>/dev/null || echo "MATLAB not found"
echo "=== Available Memory ==="
free -h
echo "=== Disk Space ==="
df -h /
```

```powershell
# Windows Diagnostic Script
Write-Host "=== System Information ==="
Get-ComputerInfo | Select WindowsProductName, WindowsVersion, TotalPhysicalMemory
Write-Host "=== Architecture ==="
[System.Environment]::Is64BitProcess
Write-Host "=== Python Version ==="
try { python --version } catch { "Python not found" }
Write-Host "=== MATLAB ==="
try { matlab -help } catch { "MATLAB not found" }
```

### Getting Help

For issues not resolved by this guide:

1. **Check System Requirements**: Ensure your system meets all compatibility requirements
2. **Review Installation Logs**: Look for specific error messages
3. **Contact BQP Support**: Provide diagnostic information and specific error messages
4. **Community Resources**: Check documentation and community forums

---

*This compatibility guide applies to both BQPhy MATLAB Toolkit and Python Library deployments. For platform-specific installation procedures, refer to the respective user guides.*



