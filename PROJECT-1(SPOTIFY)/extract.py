import ast
import re

def clean_comment(comment):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & pictographs
        "\U0001F680-\U0001F6FF"  # Transport & map symbols
        "\U0001F700-\U0001F77F"  # Alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric shapes extended
        "\U0001F800-\U0001F8FF"  # Supplemental arrows
        "\U0001F900-\U0001F9FF"  # Supplemental symbols
        "\U0001FA00-\U0001FA6F"  # Chess symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and pictographs extended
        "\U00002700-\U000027BF"  # Dingbats
        "\U00002600-\U000026FF"  # Miscellaneous symbols
        "]+",
        flags=re.UNICODE
    )
    comment = emoji_pattern.sub("", comment)
    
    # Remove social media handles (e.g., @greenday → greenday)
    comment = re.sub(r'@\w+', lambda x: x.group(0)[1:], comment)
    
   
    
    # Remove excessive whitespace, convert to lowercase
    comment = re.sub(r'\s+', ' ', comment).strip().lower()
    return comment

def extract_messages(file_path, limit=15, char_limit=350, min_length=3):
    """
    Extract up to 'limit' comments from file, clean them, and ensure they meet minimum length.
    
    Args:
        file_path (str): Path to the input file
        limit (int): Maximum number of comments to extract
        char_limit (int): Maximum length of each comment
        min_length (int): Minimum length of each comment
    
    Returns:
        list: List of cleaned, extracted comments
    """
    messages = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = ast.literal_eval(line.strip())
                    message = data.get("message", "").strip()
                    if message and len(message) >= min_length:
                        cleaned_message = clean_comment(message)[:char_limit]
                        messages.append(cleaned_message)
                        if len(messages) >= limit:
                            break
                except (SyntaxError, ValueError):
                    continue
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
    except Exception as e:
        print(f"Error reading file: {e}")
    return messages