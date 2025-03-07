#!/usr/bin/env python3
"""
Basic usage example for the Sorter SDK.

This example demonstrates how to initialize the Sorter client,
create tags and items, and perform basic operations.
"""

import os
from sorterpy import Sorter
from datetime import datetime, timedelta

def main():
    # Initialize the Sorter client with your API key
    sorter = Sorter(
        # api_key="your_api_key_here", # Obviously this should be read from an environment variable, not hardcoded.
        
        # Optionally specify a different base URL if not using the default
        # base_url="https://staging.sorter.social"
        
        # This is safer, probably do things this way.
        api_key=os.getenv("SORT_API_KEY"),
        base_url=os.getenv("SORT_BASE_URL")
    )
    
    # Create a new tag (or get existing) for categorizing items
    quality_tag = sorter.tag(
        title="image_quality",
        description="Rate images by their visual quality and clarity",
        unlisted=False  # Set to True if you want the tag to be unlisted
    )
    
    print(f"Created/retrieved tag: {quality_tag.title} (ID: {quality_tag.id})")
    
    # Create a different tag for a different attribute
    usefulness_tag = sorter.tag(
        title="image_usefulness",
        description="Rate images by their usefulness for the specific task"
    )
    
    # Add items to the quality tag (or update if they exist)
    item1 = quality_tag.item(
        title="Landscape_001.jpg",
        body="High-resolution landscape photograph with good lighting",
        url=""
    )
    
    item2 = quality_tag.item(
        title="Portrait_002.jpg",
        description="Portrait photograph with slightly blurry focus"
    )
    
    print(f"Created/updated items: {item1.title}, {item2.title}")
    
    # Record a vote between two items
    vote = quality_tag.vote(item1, 55, item2)
    print(f"Recorded vote: {vote.id} between {item1.title} and {item2.title}")
    
    # Retrieve votes for the tag with a 'since' filter
    since_time = (datetime.now() - timedelta(days=1)).isoformat()
    votes_since = quality_tag.votes(since=since_time)
    print(f"\nVotes for tag '{quality_tag.title}' since {since_time}:")
    for v in votes_since:
        print(f"- Vote ID {v.id}: {v.left_item_id} vs {v.right_item_id} with magnitude {v.magnitude}")
    
    # Update an item's properties
    updated_item = item2.update(
        title="Portrait_002_revised.jpg",
        description="Portrait photograph with improved clarity after editing"
    )
    
    print(f"Updated item: {updated_item.title}")
    
    # List all tags
    all_tags = sorter.list_tags()
    print(f"\nYou have:")
    print(f"- {len(all_tags['public'])} public tags")
    print(f"- {len(all_tags['private'])} private tags")
    print(f"- {len(all_tags['unlisted'])} unlisted tags")
    
    # List all items in a tag
    items = quality_tag.list_items()
    print(f"\nTag '{quality_tag.title}' has {len(items)} items:")
    for item in items:
        print(f"- {item.title}: {item.description}")
    
    # Reusing the tag method to get an existing tag
    existing_tag = sorter.tag(title="image_quality")
    print(f"\nRetrieved existing tag: {existing_tag.title}")


if __name__ == "__main__":
    main() 