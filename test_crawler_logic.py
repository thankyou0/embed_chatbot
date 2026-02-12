"""
Test script to demonstrate the Smart DFS crawler logic
"""
from urllib.parse import urlparse

def get_url_depth(url: str) -> int:
    """Calculate depth of URL path (number of segments)"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    return len([p for p in path.split('/') if p]) if path else 0

def get_path_similarity(url: str, reference_url: str) -> int:
    """Calculate how many path segments match between two URLs"""
    parsed1 = urlparse(url)
    parsed2 = urlparse(reference_url)
    
    path1_parts = [p for p in parsed1.path.strip('/').split('/') if p]
    path2_parts = [p for p in parsed2.path.strip('/').split('/') if p]
    
    # Count matching segments from the start
    matches = 0
    for p1, p2 in zip(path1_parts, path2_parts):
        if p1 == p2:
            matches += 1
        else:
            break
    return matches

def sort_queue_by_priority(queue: list, current_url: str):
    """Sort queue for Smart DFS: prioritize similar paths and deeper URLs"""
    if len(queue) <= 1:
        return queue
    
    def priority_score(url: str) -> tuple:
        # Higher similarity = crawl first (negative for sorting)
        similarity = -get_path_similarity(url, current_url)
        # Higher depth = crawl first (negative for sorting)
        depth = -get_url_depth(url)
        return (similarity, depth, url)
    
    return sorted(queue, key=priority_score)

# Test Example
print("=" * 80)
print("SMART DFS CRAWLER DEMONSTRATION")
print("=" * 80)

# Scenario 1: Starting from /collections
print("\n📍 Scenario 1: Crawling from /collections")
print("-" * 80)

base_url = "https://ramrajcotton.in/collections"
current = base_url

# Simulated discovered links
queue = [
    "https://ramrajcotton.in/collections/white-shirts",
    "https://ramrajcotton.in/collections/colour-shirts",
    "https://ramrajcotton.in/collections/dhotis",
    "https://ramrajcotton.in/about-us",  # This will be filtered out by path check
]

print(f"Current URL: {current}")
print(f"\nDiscovered links (unsorted):")
for i, url in enumerate(queue, 1):
    depth = get_url_depth(url)
    similarity = get_path_similarity(url, current)
    print(f"  {i}. {url}")
    print(f"     Depth: {depth}, Similarity: {similarity}")

sorted_queue = sort_queue_by_priority(queue, current)
print(f"\n✨ After Smart DFS sorting:")
for i, url in enumerate(sorted_queue, 1):
    depth = get_url_depth(url)
    similarity = get_path_similarity(url, current)
    print(f"  {i}. {url}")
    print(f"     Depth: {depth}, Similarity: {similarity}")

# Scenario 2: Now crawling from a deeper URL
print("\n\n📍 Scenario 2: Crawling from /collections/colour-shirts")
print("-" * 80)

current = "https://ramrajcotton.in/collections/colour-shirts"

queue = [
    "https://ramrajcotton.in/collections/white-shirts",  # Different category
    "https://ramrajcotton.in/collections/colour-shirts/product-1",  # Same category, deeper
    "https://ramrajcotton.in/collections/colour-shirts/product-2",  # Same category, deeper
    "https://ramrajcotton.in/collections/dhotis",  # Different category
]

print(f"Current URL: {current}")
print(f"\nDiscovered links (unsorted):")
for i, url in enumerate(queue, 1):
    depth = get_url_depth(url)
    similarity = get_path_similarity(url, current)
    print(f"  {i}. {url}")
    print(f"     Depth: {depth}, Similarity: {similarity}")

sorted_queue = sort_queue_by_priority(queue, current)
print(f"\n✨ After Smart DFS sorting:")
for i, url in enumerate(sorted_queue, 1):
    depth = get_url_depth(url)
    similarity = get_path_similarity(url, current)
    print(f"  {i}. [Priority #{i}] {url}")
    print(f"     Depth: {depth}, Similarity: {similarity}")

# Scenario 3: Expected crawl order
print("\n\n📍 Scenario 3: Complete Crawl Order Example")
print("-" * 80)
print("Starting from: https://ramrajcotton.in/collections/colour-shirts\n")

crawl_order = [
    "1. /collections/colour-shirts (start)",
    "2. /collections/colour-shirts/product-1 (deeper, same path)",
    "3. /collections/colour-shirts/product-2 (deeper, same path)",
    "4. /collections/colour-shirts/product-3 (deeper, same path)",
    "   ... (completes ALL colour-shirts products)",
    "5. /collections/colour-shirts (back to category level)",
    "   ❌ /collections/white-shirts (BLOCKED - outside path prefix)",
    "   ❌ /about-us (BLOCKED - outside path prefix)",
]

print("Expected crawl order with path restriction:")
for step in crawl_order:
    print(f"  {step}")

print("\n" + "=" * 80)
print("✅ Smart DFS ensures:")
print("  1. Only crawls URLs starting with /collections/colour-shirts")
print("  2. Completes deeper levels before moving to siblings")
print("  3. Prioritizes similar paths (finishes sections together)")
print("=" * 80)
