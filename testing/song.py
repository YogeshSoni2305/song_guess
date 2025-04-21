from tavily import TavilyClient

from extract import extract_messages

# Initialize Tavily client
tavily = TavilyClient(api_key="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")

def guess_song_name_from_comments(file_path):
    messages = extract_messages(file_path)
    if not messages:
        print("No messages found.")
        return None

    limited_messages = messages[:5]  # Reduce to avoid limit
    combined_text = "\n".join([f"User{i+1}: {msg}" for i, msg in enumerate(limited_messages)])

    question = "Based on these Instagram comments, what is the name of the song in the video?"
    query = f"{question}\nComments: {combined_text}"

    print("---- TAVILY QUERY ----")
    print(query)
    print("----------------------")

    try:
        response = tavily.qna_search(query=query)
        return response
    except Exception as e:
        print("Tavily request failed:", e)
        return None

# Run
if __name__ == "__main__":
    file_path = "C:/Users/User/Downloads/instagram_data.txt"
    result = guess_song_name_from_comments(file_path)
    print("Response:", result)
