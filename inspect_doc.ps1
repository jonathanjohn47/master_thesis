$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\Empirical Analysis of Accuracy.docx"

try {
    Write-Host "Creating Word application..."
    $word = New-Object -ComObject Word.Application
    Write-Host "Word application created."
    
    $word.Visible = $true
    Write-Host "Set Visible to true."
    
    if (-not (Test-Path $docPath)) {
        Write-Host "Error: Document not found at $docPath"
        exit
    }

    Write-Host "Opening document... $docPath"
    $doc = $word.Documents.Open($docPath)
    Write-Host "Document opened: $docPath"

    # Count Captions
    Write-Host "`n--- CAPTIONS (Style='Caption') ---"
    $captionCount = 0
    foreach ($para in $doc.Paragraphs) {
        if ($para.Style.NameLocal -eq "Caption") {
            $text = $para.Range.Text.Trim()
            if ($text -match "^Figure") {
                Write-Host "Found Caption: $text"
                $captionCount++
            }
        }
    }
    Write-Host "Total Captions Found: $captionCount"

    # Count References
    Write-Host "`n--- REFERENCES (Text='Figure X') ---"
    $rng = $doc.Content
    $find = $rng.Find
    $find.ClearFormatting()
    $find.Text = "Figure [0-9]{1,2}"
    $find.MatchWildcards = $true
    
    $refCount = 0
    while ($find.Execute()) {
        # Check if we are inside a caption (don't double count if we just iterate text)
        # Usually references are in Body Text
        if ($rng.Paragraphs[1].Style.NameLocal -ne "Caption") {
            Write-Host "Found Reference: '$($rng.Text)' in context: '$($rng.Paragraphs[1].Range.Text.Trim().Substring(0, [math]::Min(50, $rng.Paragraphs[1].Range.Text.Trim().Length))) ...'"
            $refCount++
        }
        if ($refCount -ge 20) {
            Write-Host "... showing first 20 only ..."
            break
        }
    }
    Write-Host "Total References Found (approx): $refCount (stopped at 20)"

    $doc.Close($false)
    $word.Quit()
}
catch {
    Write-Host "Error: $($_.Exception.Message)"
    Write-Host "Stack Trace: $($_.Exception.StackTrace)"
    if ($_.Exception.InnerException) {
        Write-Host "Inner Exception: $($_.Exception.InnerException.Message)"
    }
    if ($word) { $word.Quit() }
}
