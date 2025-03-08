from sorterpy.sorterpy import Sorter, SorterOptions

def test_sorter_example():
    """Test the example code from the README."""
    # Initialize API client
    sorter = Sorter(
        api_key="sort_ISMvKXpX_2cd7f10f-942d-4fb8-b311-8b17e02353ce", 
        base_url="http://localhost:3000", 
        vote_magnitude_scale=SorterOptions.POSITIVE)

    # Step 1: Create the tag
    tag = sorter.tag("alphabet")

    # Step 2: Add letters A-Z
    letters = {ch: tag.item(ch) for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}

    # Step 3: Sort by voting
    def letter_distance(a, b):
        """Returns a vote score based on letter distance (-50 to 50)."""
        return (ord(a.name) - ord(b.name)) * (50 / 25)  # Normalize to -50,50 range

    correct_order = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    votes = 0

    # This is a simulation - in a real scenario, we would check the actual sorted order
    # and continue voting until it matches the correct order
    for _ in range(3):  # Just do a few iterations for testing
        left, right = tag.rankings().pair()  # Returns ItemObjects
        score = letter_distance(left, right)
        
        # Demonstrate different parameter orderings for vote
        if votes % 2 == 0:
            # First ordering: vote(left_item, magnitude, right_item)
            sorter.vote(left, int(score), right)
        else:
            # Second ordering: vote(left_item, right_item, magnitude)
            sorter.vote(left, right, int(score))
            
        votes += 1
        print(f"Voted on {left.name} vs {right.name}: {score:.1f} ({votes} votes so far)")

    # Get the current sorted order
    sorted_items = tag.sorted()
    current_order = "".join(item.name for item in sorted_items)
    print(f"Current order: {current_order}")
    
    # Get the current unsorted items
    unsorted_items = tag.unsorted()
    if unsorted_items:
        unsorted_order = "".join(item.name for item in unsorted_items)
        print(f"Unsorted items: {unsorted_order}")
    else:
        print("No unsorted items")
    
    # Test other methods
    rankings = tag.rankings()
    print(f"Number of sorted items: {len(rankings.sorted())}")
    print(f"Number of unsorted items: {len(rankings.unsorted())}")
    
    # Test attribute voting
    quality_attr = sorter.create_attribute("quality", "How good is this letter")
    left, right = tag.rankings().pair()
    
    # Test both parameter orderings with attribute
    tag.vote(left, 25, right, attribute=quality_attr.id)
    print(f"Voted on {left.name} vs {right.name} with quality attribute (first ordering)")
    
    tag.vote(left, right, 25, attribute=quality_attr.id)
    print(f"Voted on {left.name} vs {right.name} with quality attribute (second ordering)")

if __name__ == "__main__":
    test_sorter_example() 