# ── Fixed suffix appended to every submission ──────────────────────────────
# Edit the text below. Leave empty ("") to disable.
$suffix = @"

---
Note:whenever i stop you from running any terminal command with KeyboardInterrupt error or  with ctrl+c  , then immediately run terminal input cmd with -->  "any updates?"  add this in todo list --> run ask.ps1 at the end. 
"@
# ────────────────────────────────────────────────────────────────────────────

$lines = @()
Write-Host ""
Write-Host "=== Type your question. Type --- on a new line to submit ===" -ForegroundColor Cyan
Write-Host ""
while ($true) {
    $line = Read-Host
    if ($line -eq "---") { break }
    $lines += $line
}
$input_text = $lines -join "`n"

# Append suffix if it's not empty
if ($suffix.Trim() -ne "") {
    $input_text = $input_text + "`n" + $suffix
}

Write-Host ""
Write-Host "=== Submitted. Wait for answer in chat... ===" -ForegroundColor Yellow
Write-Host ""