from extract import extract_messages
from search import search_song_info

def main():
   
    file_path = "G:\\NDA_PROJECTS\\instagram_data.txt"
    
    
    comments = extract_messages(file_path, limit=15, char_limit=350, min_length=3)
    
    if not comments:
        print("No valid comments extracted.")
        return
    
    
    print("\nExtracted Comments:")
    for i, comment in enumerate(comments, 1):
        print(f"{i}. {comment}")
    
   
    print("\nGuessing songs...")
    result = search_song_info(comments)
    
    
    print("\nAll Discussed Songs:")
    if result["all_songs"]:
        for song in result["all_songs"]:
            print(f"- \"{song['song']}\" by {song['artist']} (Likelihood: {song['likelihood']}%)")
    else:
        print("No songs identified.")
    
    
    print("\nMost Likely Song:")
    print(f"**\"{result['most_likely']['song']}\"** by **{result['most_likely']['artist']}** (Likelihood: {result['most_likely']['likelihood']}%)")

if __name__ == "__main__":
    main()