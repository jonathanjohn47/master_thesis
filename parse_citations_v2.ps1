
$inputFile = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\extracted_citations.txt"
$outputFile = "c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\citations_to_verify.json"

$lines = Get-Content $inputFile -Encoding UTF8
$citations = @()

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i].Trim()
    if (-not $line) { continue }

    # Extract all JSON blocks
    $jsonMatches = [regex]::Matches($line, 'ADDIN ZOTERO_ITEM CSL_CITATION ({.*?})(?=\s|ADDIN|$)')
    
    # Extract clean text by removing all ADDIN blocks
    $cleanText = $line -replace 'ADDIN ZOTERO_ITEM CSL_CITATION {.*?}', ''
    $cleanText = $cleanText.Trim()
    
    foreach ($match in $jsonMatches) {
        $jsonStr = $match.Groups[1].Value
        try {
            $citationData = $jsonStr | ConvertFrom-Json
            
            foreach ($item in $citationData.citationItems) {
                # Handle author
                $authors = @()
                if ($item.itemData.author) {
                    foreach ($auth in $item.itemData.author) {
                        if ($auth.family) {
                            $authors += $auth.family
                        }
                        elseif ($auth.literal) {
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
                    context = $cleanText
                    title   = $item.itemData.title
                    author  = $authors
                    year    = $year
                    id      = $item.id
                }
                $citations += $obj
            }
        }
        catch {
            # Ignore extraction errors for now
        }
    }
}

$citations | ConvertTo-Json -Depth 5 | Set-Content $outputFile -Encoding UTF8
Write-Host "Extracted $($citations.Count) citations."
