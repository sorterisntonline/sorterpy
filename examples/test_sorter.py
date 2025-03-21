from sorterpy.sorterpy import Sorter

def test_sorter_example():
    """Test the example code from the README."""
    # Load environment variables from parent directory
    import os
    from pathlib import Path
    from dotenv import load_dotenv
    
    # Load .env from parent directory
    dotenv_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path)
    
    # Initialize API client with options from environment variables
    sorter = Sorter(
        api_key=os.getenv('SORT_API_KEY', 'your-api-key'),
        base_url=os.getenv('SORT_BASE_URL', 'https://sorter.social'),
        options={
            # Choose one of the following vote_magnitude options:
            "vote_magnitude": "positive",  # Use 0-100 scale
            # "vote_magnitude": "equal",   # Use -50 to 50 scale
            "verbose": True,  # Enable detailed logging
            "quiet": False    # Don't suppress logs
        }
    )

    # Step 1: Create the tag
    tag = sorter.tag("alphabet_uniq") # FIXME: tag names are globally unique
    

    # Step 2: Add letters A-Z
    # Method 1: Using the get_or_create_item method (recommended)
    letters = {ch: tag.get_or_create_item(ch) for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
    
    # Test tag.link() method - Get link to the tag page
    tag_link = tag.link()
    print(f"Tag link: {tag_link}")
    
    # Test item.link() method - Get link to a specific item page
    item_a = letters["A"]
    item_link = item_a.link()
    print(f"Item 'A' link: {item_link}")
    
    # Method 2: Manual check for existing items (alternative approach)
    """
    # First get all existing items in the tag
    existing_items = tag.item()  # This returns all items in the tag
    existing_items_by_slug = {item.slug: item for item in existing_items}
    
    # Create a dictionary to store items, checking if they already exist by slug
    letters = {}
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        # Check if an item with this slug already exists
        # The slug is typically a lowercase version of the title with spaces replaced by hyphens
        expected_slug = ch.lower().replace(' ', '-')
        
        # Using the dictionary of existing items
        existing_item = existing_items_by_slug.get(expected_slug)
        
        # Alternative: Using the find_item_by_slug method
        # existing_item = tag.find_item_by_slug(expected_slug)
        
        if existing_item:
            # Use the existing item
            letters[ch] = existing_item
            print(f"Using existing item: {ch} (slug: {expected_slug})")
        else:
            # Create a new item
            letters[ch] = tag.item(ch)
            print(f"Created new item: {ch}")
    """

    # Step 3: Sort by voting
    def letter_distance(a, b):
        """Returns a vote score based on letter distance.
        
        For "positive" vote_magnitude (0-100 scale):
        """
        # For "positive" vote_magnitude (0-100 scale)
        raw_score = (ord(a.name) - ord(b.name)) * (50 / 25)  # Initially in -50,50 range
        return int(raw_score + 50)  # Convert to 0,100 range
        
        # For "equal" vote_magnitude (-50 to 50 scale)
        # return int((ord(a.name) - ord(b.name)) * (50 / 25))  # Normalize to -50,50 range

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
    quality_attr = sorter.attribute("quality", "How good is this letter")
    left, right = tag.rankings().pair()
    
    # Test both parameter orderings with attribute
    tag.vote(left, 25, right, attribute=quality_attr) # Now passing Attribute object directly
    print(f"Voted on {left.name} vs {right.name} with quality attribute (first ordering)")
    
    tag.vote(left, right, 25, attribute=quality_attr)
    print(f"Voted on {left.name} vs {right.name} with quality attribute (second ordering)")
    
    # Test changing options at runtime
    print("\nChanging options at runtime:")
    
    # Example of changing to "equal" vote_magnitude
    # sorter.options(vote_magnitude="equal", verbose=False)
    # print(f"New options: {sorter.options()}")
    # # Now votes should be in -50 to 50 range
    # tag.vote(left, right, 25)  # 25 in -50 to 50 scale
    # print(f"Voted on {left.name} vs {right.name} with equal scale (25)")
    
    # Example of changing to "positive" vote_magnitude
    sorter.options(vote_magnitude="positive", verbose=False)
    print(f"New options: {sorter.options()}")
    # Now votes should be in 0-100 range
    tag.vote(left, right, 75)  # 75 in 0-100 scale
    print(f"Voted on {left.name} vs {right.name} with positive scale (75)")
    
    # Test link methods with quiet mode
    print("\nLink methods with quiet mode:")
    sorter.options(quiet=True)
    
    # When quiet=True, the links are returned without printing pretty messages
    quiet_tag_link = tag.link()
    quiet_item_link = item_a.link()
    
    print(f"Tag link (quiet mode): {quiet_tag_link}")
    print(f"Item 'A' link (quiet mode): {quiet_item_link}")
    
    # Switch back to normal mode
    sorter.options(quiet=False)

if __name__ == "__main__":
    test_sorter_example() 