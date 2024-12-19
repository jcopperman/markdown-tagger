import argparse
import shutil
from pathlib import Path
import re
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate

# Initialize the language model with the specified model name
llm = Ollama(model="llama3.1:latest")

# Define paths for the report file and backup folder
REPORT_FILE = Path("tagging_report.txt")
BACKUP_FOLDER = Path("backup")

# Ensure the report file exists and write the header
REPORT_FILE.write_text("Tagging Report\n" + "=" * 50 + "\n", encoding="utf-8")

# Create the backup folder if it doesn't exist
BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)

# Function to remove HTML tags and special characters from markdown content
def clean_markdown(content: str) -> str:
    """Clean markdown content by removing HTML tags and special characters."""
    clean_text = re.sub(r"<[^>]+>", "", content)
    clean_text = re.sub(r"[^A-Za-z0-9\s]", "", clean_text)
    return " ".join(clean_text.split())

# Prompt template for generating semantic tags
PROMPT_TEMPLATE = """
You are assisting in semantic tagging of markdown files. Analyze the content to determine:
1. The content type.
2. The central themes or topics.

Provide 5–10 concise semantic tags summarizing the content's themes. Do not summarize the content itself or use verbose descriptions. Format the output like this:

<!-- Tags: ContentType: <type>, Topics: <theme1>, <theme2>, ... -->

Content:
{text}
"""

# Function to generate semantic tags using the language model
def generate_tags(content: str) -> str:
    """Generate semantic tags for the given content using the language model."""
    prompt_template = PromptTemplate(input_variables=["text"], template=PROMPT_TEMPLATE)
    prompt = prompt_template.format(text=content)
    try:
        response = llm(prompt).strip()
    except Exception as e:
        print(f"Error generating tags: {e}")
        return None

    # Debug: Display raw response from the language model
    print(f"LLM Response:\n{response}\n")

    # Extract tags from the response
    match = re.search(r"<!-- Tags:.*-->", response)
    if match:
        return match.group(0)
    else:
        print("No valid tags found in LLM response.")
        return None

# Function to process a single markdown file
def process_markdown(file_path: Path) -> None:
    """Process a markdown file to generate and insert semantic tags."""
    content = file_path.read_text(encoding="utf-8")
    clean_content = clean_markdown(content)
    print(f"Cleaned content from {file_path.name}:\n{clean_content[:500]}...\n")

    # Generate tags using the language model
    tags = generate_tags(clean_content)

    if tags:
        # Backup the original file
        backup_file_path = BACKUP_FOLDER / file_path.name
        shutil.copy(file_path, backup_file_path)

        # Prepend the generated tags to the original content
        updated_content = f"{tags}\n\n{content}"
        file_path.write_text(updated_content, encoding="utf-8")

        # Log the tagging action in the report file
        with REPORT_FILE.open("a", encoding="utf-8") as report:
            report.write(f"Tagged: {file_path} with tags: {tags}\n")
    else:
        print(f"No valid tags generated for {file_path.name}")

# Function to process all markdown files in a directory
def process_directory(directory: Path) -> None:
    """Process all markdown files in the specified directory."""
    for file_path in directory.rglob("*.md"):
        print(f"Processing {file_path.name}...")
        process_markdown(file_path)

def main() -> None:
    """Main function to parse arguments and initiate processing."""
    parser = argparse.ArgumentParser(description="Tag Markdown files using an LLM.")
    parser.add_argument("vault_directory", type=str, help="Path to markdown files")
    args = parser.parse_args()

    vault_directory = Path(args.vault_directory).resolve()
    if not vault_directory.is_dir():
        print(f"Error: Directory '{vault_directory}' does not exist.")
        return

    process_directory(vault_directory)
    print(f"Tagging complete. Report saved at '{REPORT_FILE}'.")

if __name__ == "__main__":
    main()