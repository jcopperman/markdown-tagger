### README.md
```markdown
# Markdown File Tagger

A Python script for automatically generating semantic tags for markdown files. This tool uses a language model (Ollama) to analyze the content of markdown files and prepend them with meaningful tags based on the content type and themes.

## Features
- Cleans markdown content to focus on relevant text.
- Automatically generates 5–10 semantic tags using a pre-trained language model.
- Backs up original files before modifying them.
- Logs all tagged files and their tags in a report.

## Prerequisites
1. Python 3.8 or higher.
2. Install required Python packages:
   ```bash
   pip install markdown-it-py langchain
   ```
3. A locally running Ollama instance. Update the model name in the script if necessary.

## Usage
1. Clone this repository or copy the script.
2. Run the script with the path to your markdown folder:
   ```bash
   python apply_tags.py /path/to/your/markdown/files
   ```

## Output
- **Tagged Markdown Files**: Updated markdown files with tags added at the top.
- **Backups**: Original files are saved in a `backup/` folder.
- **Tagging Report**: A summary of processed files is saved in `tagging_report.txt`.

## Example
Before processing:
```markdown
# My Blog Post
This is a blog about productivity and focus.
```

After processing:
```markdown
<!-- Tags: ContentType: Blog Post, Themes: Productivity, Focus -->

# My Blog Post
This is a blog about productivity and focus.
```

## Notes
- The tool uses a predefined template to guide the language model for generating tags.
- For best results, ensure your markdown content is well-structured and free of unnecessary metadata.

## License
This project is open-source and available under the MIT License.
```