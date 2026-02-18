
$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open($docPath)

Write-Host "Caption Labels:"
foreach ($lbl in $word.CaptionLabels) {
    Write-Host "Label: '$($lbl.Name)' (BuiltIn: $($lbl.BuiltIn))"
}

Write-Host "`nCross Reference Items (Type 2 - Figure):"
try {
    $items = $doc.GetCrossReferenceItems(2)
    Write-Host "Count via Type 2: $($items.Count)"
}
catch { Write-Host "Error Type 2: $_" }

$doc.Close($false)
$word.Quit()
