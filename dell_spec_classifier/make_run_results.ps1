$ErrorActionPreference = "Stop"

$out = "C:\Users\G\Desktop\TERESA\run_results.md"
if (Test-Path $out) { Remove-Item -Force $out }

$items = @("dl1","dl2","dl3","dl4","dl5")

foreach ($d in $items) {
  $dlDir = "C:\Users\G\Desktop\TERESA\dell_spec_classifier\output\manual_runs\$d"
  $run = Get-ChildItem -Path $dlDir -Directory -Filter "run_*" | Sort-Object Name -Descending | Select-Object -First 1
  if (-not $run) { throw "run_* not found for $d in $dlDir" }

  Add-Content -Path $out -Value ("# " + $d)
  Add-Content -Path $out -Value ("run_folder: " + $run.FullName)
  Add-Content -Path $out -Value ""
  Add-Content -Path $out -Value "## run_summary.json"
  Get-Content -Path (Join-Path $run.FullName "run_summary.json") | Add-Content -Path $out
  Add-Content -Path $out -Value ""
  Add-Content -Path $out -Value "## unknown_rows.csv"
  Get-Content -Path (Join-Path $run.FullName "unknown_rows.csv") | Add-Content -Path $out
  Add-Content -Path $out -Value ""
  Add-Content -Path $out -Value "----"
  Add-Content -Path $out -Value ""
}

Get-Item $out | Format-List FullName,Length,LastWriteTime
