<#
.SYNOPSIS
    Initializes a project repository with Git, installs dependencies, and sets up tools.

.DESCRIPTION
    This PowerShell script performs the following tasks:
    1. Initializes a Git repository
    2. Installs Python requirements from requirements.txt
    3. Initializes secrets baseline file
    4. Sets up pre-commit hooks
    5. Installs Gitleaks (a tool for detecting secrets in code)

.EXAMPLE
    .\setup_project.ps1
    Initializes the project in the current directory.
#>

function Initialize-Git {
    Write-Host "Initializing Git repository..." -ForegroundColor Cyan
    try {
        git init
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error: Failed to initialize Git repository" -ForegroundColor Red
            return $false
        }
        Write-Host "Git repository initialized successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Error initializing Git repository: $_" -ForegroundColor Red
        return $false
    }
}

function Install-Requirements {
    Write-Host "Installing Python requirements..." -ForegroundColor Cyan
    try {
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error: Failed to install requirements" -ForegroundColor Red
            return $false
        }
        Write-Host "Python requirements installed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Error installing requirements: $_" -ForegroundColor Red
        return $false
    }
}

function Initialize-SecretsBaseline {
    Write-Host "Initializing secrets baseline..." -ForegroundColor Cyan
    try {
        # Check if detect-secrets is installed
        pip show detect-secrets > $null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Installing detect-secrets..." -ForegroundColor Yellow
            pip install detect-secrets
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Error: Failed to install detect-secrets" -ForegroundColor Red
                return $false
            }
        }

        # Remove existing baseline if it exists
        if (Test-Path ".secrets.baseline") {
            Remove-Item ".secrets.baseline" -Force
            Write-Host "Removed existing .secrets.baseline file" -ForegroundColor Yellow
        }

        # Create new baseline
        detect-secrets scan > .secrets.baseline
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error: Failed to create secrets baseline file" -ForegroundColor Red
            return $false
        }

        Write-Host "Secrets baseline file initialized successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Error initializing secrets baseline: $_" -ForegroundColor Red
        return $false
    }
}

function Setup-PreCommit {
    Write-Host "Setting up pre-commit hooks..." -ForegroundColor Cyan
    try {
        pre-commit install
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error: Failed to set up pre-commit hooks" -ForegroundColor Red
            return $false
        }
        Write-Host "Pre-commit hooks installed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Error setting up pre-commit hooks: $_" -ForegroundColor Red
        return $false
    }
}

function Install-Gitleaks {
    Write-Host "Installing Gitleaks..." -ForegroundColor Cyan
    try {
        go install github.com/gitleaks/gitleaks@latest
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error: Failed to install Gitleaks" -ForegroundColor Red
            return $false
        }
        Write-Host "Gitleaks installed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Error installing Gitleaks: $_" -ForegroundColor Red
        Write-Host "Make sure Go is installed and in your PATH" -ForegroundColor Red
        return $false
    }
}

# Main script execution
Write-Host "Starting project setup..." -ForegroundColor Yellow

$gitSuccess = Initialize-Git
$reqSuccess = Install-Requirements
$baselineSuccess = Initialize-SecretsBaseline
$preCommitSuccess = Setup-PreCommit
$gitleaksSuccess = Install-Gitleaks

# Summary
Write-Host "`nSetup Summary:" -ForegroundColor Yellow
Write-Host "Git Initialization: $(if ($gitSuccess) { 'Success' } else { 'Failed' })" -ForegroundColor $(if ($gitSuccess) { 'Green' } else { 'Red' })
Write-Host "Requirements Installation: $(if ($reqSuccess) { 'Success' } else { 'Failed' })" -ForegroundColor $(if ($reqSuccess) { 'Green' } else { 'Red' })
Write-Host "Secrets Baseline Initialization: $(if ($baselineSuccess) { 'Success' } else { 'Failed' })" -ForegroundColor $(if ($baselineSuccess) { 'Green' } else { 'Red' })
Write-Host "Pre-commit Setup: $(if ($preCommitSuccess) { 'Success' } else { 'Failed' })" -ForegroundColor $(if ($preCommitSuccess) { 'Green' } else { 'Red' })
Write-Host "Gitleaks Installation: $(if ($gitleaksSuccess) { 'Success' } else { 'Failed' })" -ForegroundColor $(if ($gitleaksSuccess) { 'Green' } else { 'Red' })
