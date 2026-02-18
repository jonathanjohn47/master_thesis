
$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"
$logPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\simple_link_log.txt"

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
    
    $doc = $word.Documents.Open($docPath)
    Log-Msg "Opened."

    $rng = $doc.Content
    $find = $rng.Find
    $find.MatchWildcards = $true
    
    # We loop and force replacement
    # We must reset range after finding each one because inserting field changes range?
    # Actually, iterate carefully.
    
    $maxLoops = 500
    $i = 0
    
    while ($i -lt $maxLoops) {
        $find.Text = "Figure [0-9]{1,2}"
        $success = $find.Execute()
        
        if (-not $success) { break }
        
        # Check if inside Caption
        $style = $rng.Paragraphs.Item(1).Style.NameLocal
        if ($style -eq "Caption") { 
            # Move range forward
            $rng.Collapse(0) # wdCollapseEnd
            continue
        }
        
        # Check if field
        if ($rng.Fields.Count -gt 0) {
            $rng.Collapse(0)
            continue
        }
        
        $text = $rng.Text
        if ($text -match "(\d+)") {
            $num = $matches[1]
            # Bookmark name
            $bm = "Ref_Figure_$num"
             
            # Check bookmark validity? (assume yes for now)
            # Replace text
            # Range.Select? No, manipulate range.
             
            # Insert Field at range. 
            # Range is replaced by field.
            Log-Msg "Replacing $text with REF $bm"
             
            # wdFieldRef = 3
            $f = $doc.Fields.Add($rng, 3, "$bm \h", $true)
             
            # Range is now the field. 
            # Collapse to end of field to continue search
            # $rng is updated to field range? Yes usually.
        }
        $rng.Collapse(0) # End
        $i++
    }
    
    $doc.Fields.Update()
    $doc.Save()
    Log-Msg "Saved."
    $doc.Close()
    $word.Quit()
    
}
catch {
    Log-Msg "Error: $($_.Exception.Message)"
    if ($word) { $word.Quit() }
}
