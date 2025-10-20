# PowerShell pre-commit hook wrapper: invoke the Python analyzer script.
$repoRoot = (git rev-parse --show-toplevel) 2>$null
if (-not $repoRoot) { $repoRoot = Get-Location }
$python = $env:PYTHON -or "python"
Write-Host "Running interactive analyzer..."
$rc = & $python "$repoRoot\scripts\analyze_and_prompt.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Commit blocked by analyze_and_prompt (exit code $LASTEXITCODE). Resolve issues and try again, or use --no-verify to bypass." -ForegroundColor Yellow
    exit $LASTEXITCODE
}
exit 0