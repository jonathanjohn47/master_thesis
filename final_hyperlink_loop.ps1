
Write-Host "Starting Script..."
$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"
$logPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\hyperlink_log.txt"

function Log-Msg($msg) {
    Write-Host $msg
    try { Add-Content $logPath -Value $msg } catch {}
}

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    
    if (-not (Test-Path $docPath)) {
        Log-Msg "Doc not found"
        exit
    }
    
    Log-Msg "Opening..."
    $doc = $word.Documents.Open($docPath)
    Log-Msg "Opened."

    $rng = $doc.Content
    $find = $rng.Find
    $find.MatchWildcards = $true
    
    # Iterate all matches of "Figure [0-9]+"
    $find.Wrap = 0 # wdFindStop
    
    $count = 0
    # Use brute force loop to avoid infinite finding of same text
    # Search, if found, modify, move range.
    
    while ($true) {
        $find.Text = "Figure [0-9]{1,2}"
        $success = $find.Execute()
        
        if (-not $success) { break }
        
        # Validate match
        $text = $rng.Text
        
        # Skip if inside Caption style
        $style = try { $rng.Paragraphs.Item(1).Style.NameLocal } catch { "Unknown" }
        if ($style -eq "Caption") {
             $rng.Collapse(0) # End
             continue
        }
        
        # Skip if already Hyperlink
        if ($rng.Hyperlinks.Count -gt 0) {
             # Move past it
             $rng.Collapse(0) 
             continue
        }
        
        # Skip if field (e.g. SEQ field, though unlikely in body text)
        if ($rng.Fields.Count -gt 0) {
             $rng.Collapse(0)
             continue
        }

        # It is plain text "Figure X".
        if ($text -match "Figure (\d+)") {
             $num = $matches[1]
             $bm = "Ref_Figure_$num"
             
             # Verify bookmark exists (optional, mostly yes)
             if ($doc.Bookmarks.Exists($bm)) {
                 Log-Msg "Hyperlinking '$text' to $bm"
                 $doc.Hyperlinks.Add($rng, "", $bm)
                 $count++
             } else {
                 Log-Msg "Warning: Bookmark $bm not found."
             }
        }
        
        # Range is now the hyperlink. Collapse to end.
        $rng.Collapse(0)
    }
    
    Log-Msg "Added $count hyperlinks."
    $doc.Save()
    Log-Msg "Saved."
    $doc.Close($false)
    $word.Quit()
    
} catch {
    Log-Msg "Error: $($_.Exception.Message)"
    if ($word) { $word.Quit() }
}
