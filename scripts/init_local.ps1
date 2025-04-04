# Local development environment initialization script
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "[Step 1] Starting local environment initialization..."

# Change to backend directory
Set-Location backend
Write-Host "[Step 2] Changed to backend directory"

# Create Python virtual environment if not exists
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "[Step 3] Python virtual environment created in backend directory"
}

# Activate virtual environment
. venv/Scripts/Activate.ps1
Write-Host "[Step 4] Virtual environment activated"

# Update pip
python.exe -m pip install --upgrade pip
Write-Host "[Step 5] Pip updated to latest version"

# Install dependencies from requirements directory
Get-ChildItem "requirements/*.txt" | ForEach-Object {
    pip install -r $_.FullName
    Write-Host "[Step 6] Installed dependencies from $($_.Name)"
}

# Initialize Git configuration
git config core.autocrlf false
git config core.eol lf
Write-Host "[Step 7] Git configuration initialized"

# Return to root directory
Set-Location ..
Write-Host "[Complete] Local development environment initialization finished!" 