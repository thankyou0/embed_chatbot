# setup-hooks.ps1
# Run this ONCE after cloning the repo to activate Git hooks.
#
# Usage:
#   .\setup-hooks.ps1

Write-Host ""
Write-Host "Setting up Git hooks..." -ForegroundColor Cyan

# Tell Git to look for hooks in .githooks/ instead of .git/hooks/
git config core.hooksPath .githooks

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Git hooks configured. Hook folder: .githooks/" -ForegroundColor Green
    Write-Host ""
    Write-Host "Active hooks:" -ForegroundColor Yellow
    Get-ChildItem .githooks | ForEach-Object { Write-Host "  - $($_.Name)" }
    Write-Host ""
    Write-Host "These hooks will now run automatically on git commit, push, etc." -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] Failed to configure hooks. Are you inside the repo?" -ForegroundColor Red
}
