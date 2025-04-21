import ast

def extract_messages(file_path):
    messages = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            data = ast.literal_eval(line.strip())
            message = data.get("message")
            if message:
                messages.append(message[:350])  # Limit to 350 chars
    return messages
