$ErrorActionPreference = "Stop"

$token = [Console]::In.ReadLine()
if ([string]::IsNullOrWhiteSpace($token)) {
  throw "APIFY token was not provided on stdin."
}

$outDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$capturedAt = (Get-Date).ToUniversalTime().ToString("o")
$headers = @{ Authorization = "Bearer $token" }

$inputBody = @{
  keywords = @(
    "Back Office Executive",
    "Sales Coordinator",
    "Office Admin Executive",
    "Data Entry Executive",
    "MIS Executive",
    "Purchase Executive",
    "Procurement Executive",
    "Stores Executive",
    "Store Executive",
    "Inventory Executive",
    "Warehouse Executive",
    "Dispatch Executive",
    "Logistics Executive",
    "HR Executive",
    "Payroll Executive",
    "Accounts Executive"
  )
  location = "Ahmedabad"
  maxItems = 800
  includeDetails = $true
  sortBy = "date"
  postedWithin = "any"
  postedBy = "company"
  proxyConfiguration = @{ useApifyProxy = $true }
} | ConvertTo-Json -Depth 8

$runUri = "https://api.apify.com/v2/acts/automly~naukri-jobs-scraper/runs?maxTotalChargeUsd=2&maxItems=800&waitForFinish=300"
$run = Invoke-RestMethod -Method Post -Uri $runUri -Headers $headers -ContentType "application/json" -Body $inputBody
$runData = $run.data

$terminal = @("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT")
while ($terminal -notcontains $runData.status) {
  Start-Sleep -Seconds 10
  $runData = (Invoke-RestMethod -Method Get -Uri "https://api.apify.com/v2/actor-runs/$($runData.id)" -Headers $headers).data
}

$metadata = [ordered]@{
  captured_at = $capturedAt
  actor = "automly/naukri-jobs-scraper"
  run_id = $runData.id
  status = $runData.status
  dataset_id = $runData.defaultDatasetId
  started_at = $runData.startedAt
  finished_at = $runData.finishedAt
  usage_total_usd = $runData.usageTotalUsd
  max_total_charge_usd = 2
  max_items = 800
  search = ConvertFrom-Json $inputBody
}
$metadata | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 (Join-Path $outDir "naukri_ahmedabad_metadata.json")

if ($runData.status -ne "SUCCEEDED") {
  throw "Apify run $($runData.id) finished with status $($runData.status)."
}

$itemsUri = "https://api.apify.com/v2/datasets/$($runData.defaultDatasetId)/items?clean=true&format=json"
$items = Invoke-RestMethod -Method Get -Uri $itemsUri -Headers $headers
$items | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 (Join-Path $outDir "naukri_ahmedabad_raw.json")

function Text($value) {
  if ($null -eq $value) { return "" }
  if ($value -is [array]) { return ($value -join "; ") }
  return [string]$value
}

function Snip([string]$text, [string[]]$patterns, [int]$max = 280) {
  $clean = ((Text $text) -replace "\s+", " ").Trim()
  foreach ($pattern in $patterns) {
    $match = [regex]::Match($clean, $pattern, "IgnoreCase")
    if ($match.Success) {
      $start = [Math]::Max(0, $match.Index - 80)
      $len = [Math]::Min($clean.Length - $start, $max)
      return $clean.Substring($start, $len).Trim()
    }
  }
  if ($clean.Length -le $max) { return $clean }
  return $clean.Substring(0, $max).Trim()
}

$strongOps = "quotation|proforma|invoice|order records|customer details|enquir(y|ies)|inquir(y|ies)|follow[- ]?up|mis report|excel report|dashboard|reconciliation|purchase order|vendor|supplier|inventory|stock|warehouse|dispatch|grn|material movement|attendance|payroll|hrms|employee records|statutory compliance|leave management|data entry|back office|coordination with (sales|accounts|finance|warehouse|departments)"
$companyOps = "distributor|distribution|manufactur|factory|industrial|electrical|electronics|pharma|pharmaceutical|medical device|fmcg|retail|warehouse|supply chain|logistics|machinery|ceramic|textile|automobile spares|food|packaging|building material|components|semiconductor|trading"
$salesOnly = "field sales|direct sales|b2c sales|area sales|sales executive|sales officer|business development executive|client acquisition|cold calling|telecalling|retail sales|channel sales|loan sales|insurance sales"
$weakRole = "intern|trainee|recruiter|blue collar|teacher|faculty|doctor|nurse|developer|digital marketing|seo|graphic designer"

$rows = foreach ($item in $items) {
  $title = Text $item.title
  $company = Text $item.companyName
  $jd = Text $item.descriptionText
  $companyText = Text $item.companyDescription
  $skills = Text $item.skills
  $role = Text $item.role
  $dept = Text $item.department
  $industry = Text $item.industry
  $blob = "$title $skills $role $dept $industry $companyText $jd"

  $opsHits = ([regex]::Matches($blob, $strongOps, "IgnoreCase")).Count
  $companyHits = ([regex]::Matches($blob, $companyOps, "IgnoreCase")).Count
  $salesHits = ([regex]::Matches("$title $role $jd", $salesOnly, "IgnoreCase")).Count
  $weakHits = ([regex]::Matches("$title $role", $weakRole, "IgnoreCase")).Count

  $why = New-Object System.Collections.Generic.List[string]
  if ($opsHits -gt 0) { $why.Add("JD shows operational/admin workflow ($opsHits signal hits)") }
  if ($companyHits -gt 0) { $why.Add("company/industry looks ops-heavy") }
  if ($salesHits -gt 0) { $why.Add("caution: sales-led role") }
  if ($weakHits -gt 0) { $why.Add("caution: weak role fit") }
  if ((Text $item.postedByConsultant) -eq "True") { $why.Add("caution: consultant-posted") }

  $score = ($opsHits * 8) + [Math]::Min(18, $companyHits * 5) - ($salesHits * 12) - ($weakHits * 10)
  if ((Text $item.postedByConsultant) -eq "True") { $score -= 18 }

  $status = "NOT OUTREACH FIT"
  if ($opsHits -ge 4 -and $score -ge 28) {
    $status = "RELEVANT"
  } elseif ($opsHits -ge 2 -and $score -ge 12) {
    $status = "MAYBE"
  }

  if ($salesHits -gt 0 -and ($blob -match "quotation|invoice|order records|mis|dispatch|inventory|purchase order|vendor|supplier|warehouse")) {
    if ($status -eq "NOT OUTREACH FIT") { $status = "MAYBE" }
    $why.Add("sales title has useful ops/back-office evidence")
  }

  [pscustomobject][ordered]@{
    my_status = $status
    score = $score
    why = (($why | Select-Object -Unique) -join "; ")
    evidence = Snip $blob @("quotation|proforma|invoice|order records|customer details|enquir|follow|mis|excel report|reconciliation|purchase order|vendor|supplier|inventory|stock|warehouse|dispatch|attendance|payroll|hrms|employee records|statutory")
    captured_at = $capturedAt
    source = "Naukri via Apify automly/naukri-jobs-scraper"
    run_id = $runData.id
    source_job_id = Text $item.jobId
    company_name = $company
    job_title = $title
    posting_date = Text $item.postedAt
    location = Text $item.location
    salary = Text $item.salaryText
    experience = Text $item.experienceText
    skills = $skills
    company_url = Text $item.companyWebsite
    company_jobs_url = Text $item.companyJobsUrl
    job_url = Text $item.url
    posted_by_consultant = Text $item.postedByConsultant
    role = $role
    department = $dept
    industry = $industry
    company_description = (($companyText -replace "\r?\n", " ").Trim())
    jd_text = (($jd -replace "\r?\n", " ").Trim())
  }
}

$rows |
  Sort-Object @{ Expression = "my_status"; Descending = $false }, @{ Expression = "score"; Descending = $true }, posting_date -Descending |
  Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $outDir "naukri_ahmedabad_leads.csv")

$counts = $rows | Group-Object my_status | ForEach-Object { [pscustomobject]@{ status = $_.Name; count = $_.Count } }
[pscustomobject]@{
  run_id = $runData.id
  status = $runData.status
  dataset_id = $runData.defaultDatasetId
  usage_total_usd = $runData.usageTotalUsd
  raw_count = @($items).Count
  counts = $counts
  output_csv = (Join-Path $outDir "naukri_ahmedabad_leads.csv")
} | ConvertTo-Json -Depth 5
