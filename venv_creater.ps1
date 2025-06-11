<#
.SYNOPSIS
    Creates and activates a Python virtual environment in the current directory.

.DESCRIPTION
    This PowerShell script creates a Python virtual environment at the specified path
    and activates it within the current PowerShell session.

.PARAMETER VenvPath
    Path where the virtual environment will be created. Defaults to "venv".

.PARAMETER PythonPath
    Optional path to a specific Python executable to use. If not provided, uses the default Python.

.EXAMPLE
    .\venv_creater.ps1
    Creates a virtual environment named "venv" in the current directory and activates it.

.EXAMPLE
    .\venv_creater.ps1 -VenvPath "my_project_env"
    Creates a virtual environment named "my_project_env" in the current directory and activates it.

.EXAMPLE
    .\venv_creater.ps1 -VenvPath "custom_env" -PythonPath "C:\Python39\python.exe"
    Creates a virtual environment using the specified Python executable.
#>

param(
    [Parameter(Position=0)]
    [string]$VenvPath = "venv",

    [Parameter(Position=1)]
    [string]$PythonPath = $null
)

function Create-PythonVenv {
    param (
        [string]$VenvPath,
        [string]$PythonPath
    )

    # Create the directory if it doesn't exist
    if (-not (Test-Path $VenvPath)) {
        Write-Host "Creating directory: $VenvPath" -ForegroundColor Cyan
        New-Item -ItemType Directory -Path $VenvPath -Force | Out-Null
    }

    # Resolve the full path
    $fullVenvPath = Resolve-Path $VenvPath

    # Determine which Python executable to use
    if ([string]::IsNullOrEmpty($PythonPath)) {
        $pythonExe = "python"
        Write-Host "Using default Python executable" -ForegroundColor Cyan
    } else {
        $pythonExe = $PythonPath
        Write-Host "Using Python executable: $pythonExe" -ForegroundColor Cyan
    }

    # Test if Python is available
    try {
        $pythonVersion = & $pythonExe --version
        Write-Host "Found $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "Error: Python executable not found or not working correctly" -ForegroundColor Red
        Write-Host "Make sure Python is installed and in your PATH" -ForegroundColor Red
        return $false
    }

    # Create the virtual environment
    Write-Host "Creating virtual environment at: $fullVenvPath" -ForegroundColor Cyan
    try {
        & $pythonExe -m venv $fullVenvPath
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "Error creating virtual environment: $_" -ForegroundColor Red
        return $false
    }

    Write-Host "Virtual environment created successfully" -ForegroundColor Green
    return $true
}

function Activate-PythonVenv {
    param (
        [string]$VenvPath
    )

    $fullVenvPath = Resolve-Path $VenvPath
    $activateScript = Join-Path $fullVenvPath "Scripts\Activate.ps1"

    if (-not (Test-Path $activateScript)) {
        Write-Host "Error: Activation script not found at $activateScript" -ForegroundColor Red
        return $false
    }

    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    try {
        & $activateScript
        Write-Host "Virtual environment activated successfully" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "Error activating virtual environment: $_" -ForegroundColor Red
        return $false
    }
}

# Main script execution
$success = Create-PythonVenv -VenvPath $VenvPath -PythonPath $PythonPath
if ($success) {
    Activate-PythonVenv -VenvPath $VenvPath
}

# Print instructions for future use
Write-Host "`nTo activate this environment in the future, run:" -ForegroundColor Yellow
Write-Host "& '$(Resolve-Path $VenvPath)\Scripts\Activate.ps1'" -ForegroundColor Yellow
