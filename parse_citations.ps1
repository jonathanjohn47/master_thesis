
$inputFile = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\extracted_citations.txt"
$outputFile = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\citations_to_verify.json"

$lines = Get-Content $inputFile -Encoding UTF8
$citations = @()

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i].Trim()
    
    if ($line -match 'ADDIN ZOTERO_ITEM CSL_CITATION ({.*})') {
        $jsonStr = $matches[1]
        try {
            $citationData = $jsonStr | ConvertFrom-Json
            
            # Find context (last non-empty line before this that isn't an ADDIN line)
            $contextText = ""
            for ($j = $i - 1; $j -ge 0; $j--) {
                $prevLine = $lines[$j].Trim()
                if ($prevLine -and -not ($prevLine -match "^ADDIN")) {
                    $contextText = $prevLine
                    break
                }
            }
            
            foreach ($item in $citationData.citationItems) {
                # Handle author which can be an array of objects or just objects
                $authors = @()
                if ($item.itemData.author) {
                    foreach ($auth in $item.itemData.author) {
                        if ($auth.family) {
                            $authors += $auth.family
                        } elseif ($auth.literal) {
                            $authors += $auth.literal
                        }
                    }
                }

                # Handle date
                $year = ""
                if ($item.itemData.issued.'date-parts') {
                   $year = $item.itemData.issued.'date-parts'[0][0]
                }
                
                $obj = [PSCustomObject]@{
                    context = $contextText
                    title = $item.itemData.title
                    author = $authors
                    year = $year
                    id = $item.id
                }
                $citations += $obj
            }
        }
        catch {
            Write-Warning "Failed to parse JSON at line $($i+1): $_"
        }
    }
}

$citations | ConvertTo-Json -Depth 5 | Set-Content $outputFile -Encoding UTF8
Write-Host "Extracted $($citations.Count) citations."
