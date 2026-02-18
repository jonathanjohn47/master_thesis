
$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open($docPath)

Write-Host "--- Inspecting Bookmarks ---"
$bmCount = $doc.Bookmarks.Count
Write-Host "Total Bookmarks: $bmCount"
if ($bmCount -gt 0) {
    $bm = $doc.Bookmarks.Item(1)
    Write-Host "Sample Bookmark 1: $($bm.Name)"
}

Write-Host "`n--- Inspecting Fields ---"
$fieldCount = $doc.Fields.Count
Write-Host "Total Fields: $fieldCount"

# Check for REF fields
$refFields = 0
foreach ($f in $doc.Fields) {
    if ($f.Code.Text -match "REF") {
        $refFields++
        if ($refFields -lt 5) {
            Write-Host "Found REF Field: '$($f.Code.Text)' -> Result: '$($f.Result.Text)'"
        }
    }
}
Write-Host "Total REF Fields found: $refFields"

Write-Host "`n--- Inspecting Text 'Figure 13' ---"
$rng = $doc.Content
$find = $rng.Find
$find.Text = "Figure 13"
if ($find.Execute()) {
    Write-Host "Found text 'Figure 13'"
    Write-Host "In Paragraph Style: $($rng.Paragraphs.Item(1).Style.NameLocal)"
    Write-Host "Range Field Count: $($rng.Fields.Count)"
    if ($rng.Fields.Count -gt 0) {
        Write-Host "It IS inside a field."
    }
    else {
        Write-Host "It is NOT inside a field (Plain Text)."
    }
}
else {
    Write-Host "Could not find text 'Figure 13'"
}

$doc.Close($false)
$word.Quit()
