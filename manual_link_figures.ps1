
$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"
$logPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\manual_link_log.txt"

function Log-Msg($msg) {
    Write-Host $msg
    Add-Content $logPath -Value $msg
}

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $true
    
    if (-not (Test-Path $docPath)) {
        Log-Msg "Error: Document not found."
        exit
    }

    Log-Msg "Opening document..."
    $doc = $word.Documents.Open($docPath)
    
    # ---------------------------------------------------------
    # PART 1: BOOKMARK CAPTIONS
    # ---------------------------------------------------------
    Log-Msg "Bookmarking captions..."
    
    $bookmarksCreated = @{} # Map Number -> BookmarkName
    
    foreach ($para in $doc.Paragraphs) {
        $text = $para.Range.Text.Trim()
        # "Figure 1 Something" or "Figure 1" (if just label field + text)
        # Note: The field result might be in the text.
        
        # We need to extract the number.
        if ($text -match "^Figure\s+(\d+)") {
            $num = [int]$matches[1]
            $bmName = "Ref_Figure_$num"
             
            # Check if this paragraph is actually a caption style?
            # Or if it contains a SEQ field.
            if ($para.Range.Fields.Count -gt 0) {
                # Add bookmark to the whole paragraph range
                $doc.Bookmarks.Add($bmName, $para.Range)
                $bookmarksCreated[$num] = $bmName
                Log-Msg "Bookmarked Figure $num as $bmName"
            }
        }
    }
    
    Log-Msg "Created $($bookmarksCreated.Count) bookmarks."
    
    # ---------------------------------------------------------
    # PART 2: INSERT REF FIELDS
    # ---------------------------------------------------------
    Log-Msg "Linking references..."
    
    if ($bookmarksCreated.Count -gt 0) {
        $rng = $doc.Content
        $find = $rng.Find
        $find.ClearFormatting()
        $find.Text = "Figure [0-9]{1,2}"
        $find.MatchWildcards = $true
        $find.Wrap = 0 
        
        while ($find.Execute()) {
            # Skip if inside Caption style
            $styleName = try { $rng.Paragraphs.Item(1).Style.NameLocal } catch { "Unknown" }
            if ($styleName -eq "Caption") { continue }
            
            # Skip if already a field
            if ($rng.Fields.Count -gt 0) { continue }
            
            $matchText = $rng.Text
            if ($matchText -match "Figure (\d+)") {
                $refNum = [int]$matches[1]
                
                if ($bookmarksCreated.ContainsKey($refNum)) {
                    $bmName = $bookmarksCreated[$refNum]
                    Log-Msg "Linking '$matchText' to $bmName"
                    
                    # Insert REF field
                    # Field text: "REF Ref_Figure_N \h"
                    # We select the range and add field
                    $rng.Select()
                    $word.Selection.Fields.Add($word.Selection.Range, -1, "REF $bmName \h", $false) 
                    # -1 = wdFieldEmpty? No, wdFieldRef = 3. 
                    # Actually, Type is int. wdFieldRef = 3.
                    # Text is instructions.
                    
                    # Let's use Type=-1 (Empty) and text="REF $bmName \h"
                    # Or specific Type=3.
                    # $doc.Fields.Add(Range, Type, Text, PreserveFormatting)
                }
                else {
                    Log-Msg "Warning: No bookmark for Figure $refNum"
                }
            }
        }
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
