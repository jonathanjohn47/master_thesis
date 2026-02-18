import json
from collections import defaultdict

def find_citation_clusters(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {json_path}")
        return

    # Group citations by context
    context_clusters = defaultdict(list)
    for entry in data:
        context = entry.get('context', '').strip()
        if context:
            context_clusters[context].append(entry)

    print(f"Found {len(context_clusters)} unique contexts.")

    # Filter for clusters with many citations (likely stuffing)
    citation_stuffing_threshold = 5 
    
    stuffed_contexts = []
    for context, items in context_clusters.items():
        if len(items) >= citation_stuffing_threshold:
            stuffed_contexts.append({
                'context': context,
                'count': len(items),
                'citations': [f"{item.get('author', ['Unknown'])[0]} ({item.get('year', '????')})" for item in items]
            })

    # Sort by count descending
    stuffed_contexts.sort(key=lambda x: x['count'], reverse=True)

    print(f"\nFound {len(stuffed_contexts)} paragraphs with >= {citation_stuffing_threshold} citations.\n")

    for i, item in enumerate(stuffed_contexts, 1):
        print(f"--- Block {i} (Count: {item['count']}) ---")
        # Print first 200 chars of context to identify the paragraph
        print(f"Paragraph Start: {item['context'][:200]}...") 
        print(f"Citations: {', '.join(item['citations'][:5])} ... and {len(item['citations'])-5} more")
        print("\n")

if __name__ == "__main__":
    find_citation_clusters(r'c:\Users\jonat\OneDrive\Documents\GitHub\master_thesis\citations_to_verify.json')
