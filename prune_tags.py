import os
import re
import argparse

# Function to clean and remove all tags (even malformed or nested)
def clean_tags_from_content(content):
    """Remove all tags from the markdown content, including malformed and nested tags."""
    # Regex to find and remove all instances of <!-- Tags: ... -->
    cleaned_content = re.sub(r'<!--\s*Tags:.*?-->', '', content, flags=re.DOTALL)
    return cleaned_content

# Function to process each markdown file
def process_markdown_file(file_path):
    """Process markdown file to remove its tags."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove all tags (including malformed or nested)
    cleaned_content = clean_tags_from_content(content)

    # Save the cleaned content back to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(cleaned_content)
    
    print(f"Cleaned tags in: {file_path}")

# Function to process all markdown files in the provided vault directory
def clean_up_vault_tags(vault_directory):
    """Iterate through all markdown files and clean up tags."""
    # Walk through the vault directory to find all .md files
    for dirpath, _, filenames in os.walk(vault_directory):
        for filename in filenames:
            if filename.endswith(".md"):
                file_path = os.path.join(dirpath, filename)
                process_markdown_file(file_path)

# Main function to handle command-line arguments and run the script
def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Remove all tags from markdown files.")
    parser.add_argument("vault_directory", type=str, help="Path to the markdown vault directory")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if the provided directory path is valid
    if not os.path.isdir(args.vault_directory):
        print(f"Error: The directory {args.vault_directory} does not exist or is not a directory.")
        return
    
    # Run the cleaning process
    clean_up_vault_tags(args.vault_directory)
    print("Tag removal complete.")

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()