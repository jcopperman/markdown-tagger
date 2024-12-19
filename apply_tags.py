import argparse
import shutil
from pathlib import Path
import re
from langchain_community.llms import Ollama  # Updated import
from langchain.prompts import PromptTemplate
import warnings

# Suppress deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Initialize the language model with the specified model name
llm = Ollama(model="llama3.1:latest")

# Define paths for the report file and backup folder
REPORT_FILE = Path("tagging_report.txt")
BACKUP_FOLDER = Path("backup")

# Define the prompt template that was missing in the original code
PROMPT_TEMPLATE = """
You are assisting in semantic tagging of markdown files. Analyze the content to determine:
1. The content type.
2. The central themes or topics.
Provide 5–10 concise semantic tags summarizing the content's themes. Format the output exactly like this:

<!-- Tags: ContentType: <type>, Topics: <theme1>, <theme2>, ... -->

Content:
{text}
"""

# Ensure the report file exists and write the header
REPORT_FILE.write_text("Tagging Report\n" + "=" * 50 + "\n", encoding="utf-8")

# Create the backup folder if it doesn't exist
BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)

def clean_markdown(content: str) -> str:
    """Clean markdown content by removing HTML tags while preserving markdown syntax."""
    try:
        # Remove HTML tags except for the Tags comment
        tag_pattern = r"<!-- Tags:.*?-->"
        existing_tags = re.findall(tag_pattern, content, re.DOTALL)
        clean_text = re.sub(r"<[^>]+>", "", content)
        # Restore any existing tags that were removed
        for tag in existing_tags:
            clean_text = tag + "\n" + clean_text
        # Preserve only alphanumeric characters and markdown syntax
        clean_text = re.sub(r"[^\w\s#\*\-:]", "", clean_text)
        return " ".join(clean_text.split())
    except Exception as e:
        print(f"Error cleaning markdown: {e}")
        return content

def has_tags(content: str) -> bool:
    """Check if the content already has semantic tags."""
    try:
        return bool(re.search(r"<!-- Tags:.*?-->", content, re.DOTALL))
    except Exception as e:
        print(f"Error checking for tags: {e}")
        return False

def generate_tags(content: str) -> str:
    """Generate semantic tags for the given content using the language model."""
    try:
        prompt_template = PromptTemplate(input_variables=["text"], template=PROMPT_TEMPLATE)
        prompt = prompt_template.format(text=content[:1000])  # Limit content length to avoid token limits
        
        response = llm(prompt).strip()
        print(f"LLM Response: {response}")  # Debug: Print the raw response from LLM
        
        # Extract just the tag section if the response contains additional text
        tag_match = re.search(r"(<!-- Tags:.*?-->)", response, re.DOTALL)
        if tag_match:
            return tag_match.group(1)
        else:
            print(f"Error: Could not find tags in LLM response")
            return None
            
    except Exception as e:
        print(f"Error generating tags: {e}")
        return None

def process_markdown(file_path: Path) -> None:
    """Process a markdown file to generate and insert semantic tags."""
    try:
        print(f"Processing file: {file_path}")
        
        # Skip files that are too large (optional, adjust size as needed)
        if file_path.stat().st_size > 1_000_000:  # Skip files larger than 1MB
            print(f"Skipping {file_path.name}: File too large")
            return
            
        content = file_path.read_text(encoding="utf-8")
        
        # Only process files without existing tags
        if not has_tags(content):
            clean_content = clean_markdown(content)
            print(f"Cleaned content preview from {file_path.name}:\n{clean_content[:200]}...\n")

            # Generate tags using the language model
            tags = generate_tags(clean_content)

            if tags:
                # Backup the original file
                backup_file_path = BACKUP_FOLDER / file_path.name
                shutil.copy(file_path, backup_file_path)

                # Prepend the generated tags to the original content
                updated_content = f"{tags}\n\n{content}"

                # Write the updated content with the tags
                file_path.write_text(updated_content, encoding="utf-8")

                # Log the tagging action in the report file
                with REPORT_FILE.open("a", encoding="utf-8") as report:
                    report.write(f"Tagged: {file_path} with tags: {tags}\n")
            else:
                print(f"No valid tags generated for {file_path.name}")
        else:
            print(f"Skipping {file_path.name}: Already has tags")
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")

def process_directory(directory: Path) -> None:
    """Process all markdown files in the specified directory."""
    try:
        for file_path in directory.rglob("*.md"):
            print(f"Processing {file_path.name}...")
            process_markdown(file_path)
    except Exception as e:
        print(f"Error processing directory {directory}: {e}")

def main() -> None:
    """Main function to parse arguments and initiate processing."""
    parser = argparse.ArgumentParser(description="Tag Markdown files using an LLM.")
    parser.add_argument("vault_directory", type=str, help="Path to markdown files")
    args = parser.parse_args()

    try:
        vault_directory = Path(args.vault_directory).resolve()
        if not vault_directory.is_dir():
            print(f"Error: Directory '{vault_directory}' does not exist.")
            return

        process_directory(vault_directory)
        print(f"Tagging complete. Report saved at '{REPORT_FILE}'.")
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()