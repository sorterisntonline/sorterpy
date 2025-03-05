#!/usr/bin/env python3
"""
Basic usage example for the Sorter SDK.

This example demonstrates how to initialize the Sorter client,
create a project, tags, and items, and perform basic operations.
"""

from sorterpy import Sorter

def main():
    # Initialize the Sorter client with your API key
    sorter = Sorter(
        #api_key="your_api_key_here", # Obviously this should be read from an environment variable, not hardcoded.
        # Optionally specify a different base URL if not using the default
        # base_url="https://staging.sorter.social"
    )

    # Create or select a project by name
    # The project name is used as the namespace for organizing tags
    project = sorter.project("ml_image_dataset")
    
    # Create a new tag for categorizing items
    quality_tag = project.create_tag(
        title="image_quality",
        description="Rate images by their visual quality and clarity",
        unlisted=False  # Set to True if you want the tag to be unlisted
    )
    
    print(f"Created tag: {quality_tag.title} (ID: {quality_tag.id})")
    
    # Create a different tag for a different attribute
    usefulness_tag = project.create_tag(
        title="image_usefulness",
        description="Rate images by their usefulness for the specific task"
    )
    
    # Add items to the quality tag
    item1 = quality_tag.create_item(
        title="Landscape_001.jpg",
        description="High-resolution landscape photograph with good lighting"
    )
    
    item2 = quality_tag.create_item(
        title="Portrait_002.jpg",
        description="Portrait photograph with slightly blurry focus"
    )
    
    print(f"Created items: {item1.title}, {item2.title}")
    
    # Update an item's properties
    updated_item = item2.update(
        title="Portrait_002_revised.jpg",
        description="Portrait photograph with improved clarity after editing"
    )
    
    print(f"Updated item: {updated_item.title}")
    
    # List all tags in the project
    all_tags = project.list_tags()
    print(f"\nProject has:")
    print(f"- {len(all_tags['public'])} public tags")
    print(f"- {len(all_tags['private'])} private tags")
    print(f"- {len(all_tags['unlisted'])} unlisted tags")
    
    # List all items in a tag
    items = quality_tag.list_items()
    print(f"\nTag '{quality_tag.title}' has {len(items)} items:")
    for item in items:
        print(f"- {item.title}: {item.description}")
    
    # Get an existing tag by title
    existing_tag = project.get_tag(title="image_quality")
    if existing_tag:
        print(f"\nRetrieved existing tag: {existing_tag.title}")


if __name__ == "__main__":
    main() 