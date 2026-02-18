
$xmlPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\temp_dir\word\document.xml"
$backupPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\temp_dir\word\document.xml.bak"
$newDocxPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\Empirical Analysis of Accuracy_Cleaned.docx"
$sourceDir = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\temp_dir"

if (-not (Test-Path $xmlPath)) {
    Write-Host "Error: document.xml not found."
    exit
}

Copy-Item $xmlPath $backupPath -Force

$content = Get-Content $xmlPath -Raw

# Definition of garbage citations to remove
# We target the text "Author, Year;" or "Author, Year"
# We handle the semicolon and spacing.

$garbage = @(
    "Abbaszadi, 2025",
    "Akon et al., 2008",
    "Butt et al., 2003",
    "Fu & Wang, 2009",
    "Ma et al., 2014", 
    "Panisson et al., 2006",
    "Wu et al., 2014",
    "Maher & Nasr, 2021",
    "Urblik et al., 2023",
    "Zhang et al., 2023",
    "Zhou et al., 2024",
    "Song et al., 2022",
    "Hosseinalipour et al., 2020",
    "Dhaouadi et al., 2025",
    "Jing & Wang, 2024",
    "Weng et al., 2023",
    "Adekola & Dada, 2024",
    "Herzog & Herzog, 2024",
    "Satilmisoglu & Keskin, 2023",
    "Bondok et al., 2023",
    "Teryak et al., 2023"
    # Skipped ambiguous ones like "Ali" to be safe
)

$count = 0

foreach ($term in $garbage) {
    # Patterns to try:
    # 1. "; $term" (middle/end)
    # 2. "$term; " (start)
    # 3. "$term" (if alone) - risky? No, replacing with nothing leaves empty parens "()"? 
    # Better to leave empty parens than keep garbage.
    
    # Simple replace: "; $term" -> ""
    if ($content.Contains("; $term")) {
        $content = $content.Replace("; $term", "")
        $count++
        Write-Host "Removed: ; $term"
    }
    
    # Replace: "$term; " -> ""
    if ($content.Contains("$term; ")) {
        $content = $content.Replace("$term; ", "")
        $count++
        Write-Host "Removed: $term; "
    }
    
    # Replace: "$term" -> "" (Last resort, might leave trailing chars)
    # Only if previous didn't match? No, can effectively clean up.
    # But check if we already removed it?
    # Let's just try to be specific.
}

# Special handling for "J. Yang, 2024" (Real Estate) vs others
# "J. Yang, 2024" is specific.
if ($content.Contains("; J. Yang, 2024")) {
    $content = $content.Replace("; J. Yang, 2024", "")
    $count++
    Write-Host "Removed: ; J. Yang, 2024"
}

$content | Set-Content $xmlPath -NoNewline

Write-Host "Total removals: $count"

# Repackage
if (Test-Path $newDocxPath) { Remove-Item $newDocxPath -Force }

Compress-Archive -Path "$sourceDir\*" -DestinationPath $newDocxPath -Force
Write-Host "Created cleaned docx at $newDocxPath"
