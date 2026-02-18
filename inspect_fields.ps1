
$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open($docPath)

Write-Host "Checking paragraphs for fields..."
foreach ($para in $doc.Paragraphs) {
    $text = $para.Range.Text.Trim()
    if ($text -match "^Figure") {
        Write-Host "Found Figure Paragraph: '$text'"
        Write-Host "  Style: $($para.Style.NameLocal)"
        Write-Host "  Field Count: $($para.Range.Fields.Count)"
        if ($para.Range.Fields.Count -gt 0) {
            foreach ($f in $para.Range.Fields) {
                Write-Host "    Field Code: $($f.Code.Text)"
            }
        }
    }
}

$doc.Close($false)
$word.Quit()
