<#
.SYNOPSIS
    Fixes issues with the secrets baseline file for pre-commit hooks.

.DESCRIPTION
    This PowerShell script attempts to fix issues with the .secrets.baseline file
    by regenerating it, verifying its format, and ensuring it's properly placed in the repo.

.EXAMPLE
    .\fix_secrets_baseline.ps1
    Fixes the secrets baseline file in the current directory.
#>

# Make sure we're in the repository root
$repoRoot = git rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Not in a git repository. Please run this script from a git repository." -ForegroundColor Red
    exit 1
}

# Change to repository root
Set-Location $repoRoot
Write-Host "Working in repository root: $repoRoot" -ForegroundColor Cyan

# Check if detect-secrets is installed
$detectSecretsInstalled = $false
try {
    $null = & detect-secrets --version
    $detectSecretsInstalled = $true
} catch {
    Write-Host "detect-secrets not found. Installing..." -ForegroundColor Yellow
    pip install detect-secrets
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install detect-secrets" -ForegroundColor Red
        exit 1
    }
}

# Remove existing baseline if it exists
if (Test-Path ".secrets.baseline") {
    Write-Host "Removing existing .secrets.baseline file..." -ForegroundColor Yellow
    Remove-Item ".secrets.baseline" -Force
}

# Create new baseline
Write-Host "Creating new secrets baseline..." -ForegroundColor Cyan
& detect-secrets scan --all-files | Out-File -Encoding utf8 -FilePath .secrets.baseline
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to create secrets baseline file" -ForegroundColor Red
    exit 1
}

# Verify the baseline file
if (-not (Test-Path ".secrets.baseline")) {
    Write-Host "Error: Failed to create .secrets.baseline file" -ForegroundColor Red
    exit 1
}

Write-Host "Verifying baseline file..." -ForegroundColor Cyan
$baselineContent = Get-Content ".secrets.baseline" -Raw
try {
    $null = $baselineContent | ConvertFrom-Json
    Write-Host "Baseline file is valid JSON" -ForegroundColor Green
} catch {
    Write-Host "Error: .secrets.baseline is not valid JSON" -ForegroundColor Red
    exit 1
}

# Test the pre-commit hook directly
Write-Host "Testing detect-secrets hook..." -ForegroundColor Cyan
$hookTest = & detect-secrets-hook --baseline .secrets.baseline 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: detect-secrets-hook test failed with error:" -ForegroundColor Yellow
    Write-Host $hookTest -ForegroundColor Yellow

    # Fix for specific path issue
    Write-Host "Attempting to fix path issue..." -ForegroundColor Cyan

    # Make a copy with absolute path
    $absolutePath = Join-Path -Path $repoRoot -ChildPath ".secrets.baseline"

    # Update pre-commit config to use absolute path
    $preCommitConfig = Get-Content ".pre-commit-config.yaml" -Raw
    $preCommitConfig = $preCommitConfig -replace "args: \['--baseline', '\.secrets\.baseline'\]", "args: ['--baseline', '$($absolutePath -replace '\\', '\\')']"
    $preCommitConfig | Set-Content ".pre-commit-config.yaml"

    Write-Host "Updated pre-commit config with absolute path" -ForegroundColor Green
} else {
    Write-Host "detect-secrets hook test passed" -ForegroundColor Green
}

Write-Host "`nFix completed. Try committing again." -ForegroundColor Green
Write-Host "If you still encounter issues, try running: pre-commit run detect-secrets --all-files" -ForegroundColor Yellow
