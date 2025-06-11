<#
.SYNOPSIS
    Guides the user to create a private GitHub repository and sets it as the remote origin.

.DESCRIPTION
    This script helps set up a remote GitHub repository for the current local Git repository.
    It determines the desired repository name, instructs the user to create it manually
    on GitHub (as private and empty), prompts for the repository's HTTPS URL,
    adds it as the 'origin' remote, and attempts the initial push.

.NOTES
    Requires Git to be installed and configured.
    Does not require the GitHub CLI ('gh').
    Relies on user manually creating the repository via the GitHub web interface.
    Browser-based authentication will likely be triggered during the 'git push' step.

.EXAMPLE
    .\setup_github_remote.ps1
    Runs the guided setup process in the current directory.
#>

# --- Configuration ---
$defaultRemoteName = 'origin'

# --- Functions ---
function Test-IsGitRepository {
    git rev-parse --is-inside-work-tree 2>$null
    return $LASTEXITCODE -eq 0
}

function Get-CurrentBranchName {
    $branchName = git rev-parse --abbrev-ref HEAD 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning 'Could not determine the current branch name. Defaulting to main.'
        return 'main' # Default branch name
    }
    return $branchName.Trim()
}

# --- Main Script ---

# 1. Check if it's a Git repository
if (-not (Test-IsGitRepository)) {
    Write-Error 'This directory does not appear to be a Git repository. Please run git init first.'
    exit 1
}
Write-Host 'Current directory is a Git repository.' -ForegroundColor Green

# 2. Determine Repository Name
$repoName = (Get-Location).ProviderPath.Split('\')[-1]
Write-Host "Using repository name: '$repoName' (based on current folder name)." -ForegroundColor Cyan

# 3. Check for existing remote
$existingRemote = git remote get-url $defaultRemoteName 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Warning "A remote named '$defaultRemoteName' already exists: $existingRemote"
    $confirmation = Read-Host 'Do you want to remove the existing remote and continue? (y/N)'
    if ($confirmation -ne 'y') {
        Write-Host 'Aborting script.' -ForegroundColor Yellow
        exit 0
    }
    Write-Host "Removing existing remote '$defaultRemoteName'..." -ForegroundColor Yellow
    git remote remove $defaultRemoteName
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to remove existing remote '$defaultRemoteName'. Please remove it manually and try again."
        exit 1
    }
}

# 4. Instruct User for Manual Creation
Write-Host ''
Write-Host 'Please create the repository manually on GitHub:' -ForegroundColor Yellow
Write-Host ' 1. Go to https://github.com/new' -ForegroundColor Yellow

# Open GitHub new repository page in the default browser
Write-Host 'Opening GitHub new repository page in your browser...' -ForegroundColor Cyan
Start-Process 'https://github.com/new'

Write-Host " 2. Repository name: '$repoName'" -ForegroundColor Yellow
Write-Host " 3. Ensure 'Private' is selected." -ForegroundColor Yellow
Write-Host ' 4. IMPORTANT: *Do not* initialize with a README, .gitignore, or license.' -ForegroundColor Red
Write-Host " 5. Click 'Create repository'." -ForegroundColor Yellow
Write-Host " 6. On the next page, under 'or push an existing repository from the command line', copy the HTTPS URL." -ForegroundColor Yellow
Write-Host "    (It should look like: https://github.com/YOUR_USERNAME/$repoName.git)" -ForegroundColor Yellow
Write-Host ''

# 5. Prompt for URL
$repoUrl = Read-Host 'Paste the HTTPS URL of your new GitHub repository here'

# 6. Validate URL (basic check)
if (-not ($repoUrl -like 'https://github.com/*/*.git')) {
    Write-Error "The provided URL '$repoUrl' does not look like a valid GitHub HTTPS repository URL. Please check and try again."
    exit 1
}

# 7. Add Remote
Write-Host "Adding remote '$defaultRemoteName' with URL: $repoUrl" -ForegroundColor Cyan
try {
    git remote add $defaultRemoteName $repoUrl
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to add remote '$defaultRemoteName'."
        exit 1
    }
    Write-Host "Remote '$defaultRemoteName' added successfully." -ForegroundColor Green
} catch {
    $errorMessage = $_.Exception.Message
    Write-Error "An error occurred while adding the remote: $errorMessage"
    exit 1
}

# 8. Initial Push
$currentBranch = Get-CurrentBranchName
Write-Host "Attempting to push the current branch ('$currentBranch') to '$defaultRemoteName'..." -ForegroundColor Cyan
Write-Host '(This may trigger a browser login prompt from Git Credential Manager)' -ForegroundColor Yellow
try {
    git push -u $defaultRemoteName $currentBranch
    if ($LASTEXITCODE -ne 0) {
        Write-Error 'Failed to push to the remote repository. Check Git output for details.'
        # Don't exit here, the remote might still be set correctly
    } else {
        Write-Host "Initial push successful. Local branch '$currentBranch' is tracking '$defaultRemoteName/$currentBranch'." -ForegroundColor Green
    }
} catch {
    $errorMessage = $_.Exception.Message
    Write-Error "An error occurred during the push operation: $errorMessage"
}

Write-Host ''
Write-Host 'Setup complete.' -ForegroundColor Green
