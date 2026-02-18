
$docPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\MASTER THESIS_cleaned.docx"
$logPath = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\force_link_log.txt"

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
    # PART 1: ENSURE BOOKMARKS EXIST (Re-run bookmarking just in case)
    # ---------------------------------------------------------
    Log-Msg "Scanning for captions to bookmark..."
    $bookmarksCreated = @{}
    
    foreach ($para in $doc.Paragraphs) {
        $text = $para.Range.Text.Trim()
        # Look for the SEQ field result. 
        # But para.Range.Text might include the field result.
        
        if ($text -match "^Figure\s+(\d+)") {
            $num = [int]$matches[1]
            $bmName = "Ref_Figure_$num"
             
            if ($para.Range.Fields.Count -gt 0) {
                if (-not $doc.Bookmarks.Exists($bmName)) {
                    $doc.Bookmarks.Add($bmName, $para.Range)
                    Log-Msg "Added missing bookmark: $bmName"
                }
                $bookmarksCreated[$num] = $bmName
            }
        }
    }
    Log-Msg "Bookmarks ready: $($bookmarksCreated.Count)"

    # ---------------------------------------------------------
    # PART 2: FORCE REPLACE TEXT WITH REF FIELDS
    # ---------------------------------------------------------
    Log-Msg "Linking references..."
    
    $rng = $doc.Content
    $find = $rng.Find
    $find.ClearFormatting()
    $find.Text = "Figure [0-9]{1,2}"
    $find.MatchWildcards = $true
    $find.Wrap = 0 
    
    while ($find.Execute()) {
        # Check style
        $styleName = try { $rng.Paragraphs.Item(1).Style.NameLocal } catch { "Unknown" }
        if ($styleName -eq "Caption") { continue }
        
        # Check if already a field
        if ($rng.Fields.Count -gt 0) { continue }
        
        $matchText = $rng.Text
        if ($matchText -match "Figure (\d+)") {
            $refNum = [int]$matches[1]
            
            if ($bookmarksCreated.ContainsKey($refNum)) {
                $bmName = "Ref_Figure_$refNum"
                Log-Msg "Replacing '$matchText' with REF $bmName"
                
                # CRITICAL FIX: Delete text, then Insert Field
                # But Field.Add replaces the range if range is not collapsed?
                # Let's try explicit logic.
                
                # $rng is the range of "Figure X".
                # Expand range slightly if needed? No.
                
                # Insert Field
                # Type 3 = wdFieldRef
                # Text = "Ref_Figure_1 \h"
                
                $field = $doc.Fields.Add($rng, 3, "$bmName \h", $true)
                
                # Verify
                if ($field) {
                    # Log-Msg "Field inserted."
                }
                else {
                    Log-Msg "FAILED to insert field."
                }
            }
        }
    }
    
    Log-Msg "Updating fields..."
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
