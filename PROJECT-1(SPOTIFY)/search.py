import os
import requests
from groq import Groq
from dotenv import load_dotenv
from collections import Counter
import json

load_dotenv()

def parse_failed_generation(failed_text):
    """
    Attempt to parse the failed JSON generation from Groq to extract songs.
    
    Args:
        failed_text (str): The failed JSON string
    
    Returns:
        list: List of song-artist dicts, or empty list if parsing fails
    """
    try:
        # Clean the text by removing invalid tokens
        cleaned_text = failed_text.replace('scriptId', '')
        # Attempt to parse as JSON
        parsed = json.loads(cleaned_text)
        return parsed.get("songs", [])
    except Exception as e:
        print(f"Failed to parse failed_generation: {e}")
        return []

def compute_likelihood(songs, comments):
    """
    Compute likelihood scores for songs based on frequency, clarity, and context.
    
    Args:
        songs (list): List of dicts with song and artist
        comments (list): List of comments
    
    Returns:
        list: Songs with added 'likelihood' field
    """
    # Count frequency of song mentions
    song_counts = Counter(song['song'].lower() for song in songs)
    
    # Assign likelihood scores
    for song in songs:
        score = 0
        song_name = song['song'].lower()
        
        # Frequency (50% weight)
        frequency_score = (song_counts[song_name] / len(songs)) * 50
        
        # Clarity (30% weight): Clear song-artist pairs get higher scores
        clarity_score = 30 if song.get('artist') and song['artist'] != "Unknown" else 15
        
        # Context (20% weight): Check if song appears in comments explicitly
        context_score = 20 if any(song_name in comment.lower() for comment in comments) else 10
        
        score = frequency_score + clarity_score + context_score
        song['likelihood'] = round(score, 2)
    
    # Sort by likelihood (descending)
    return sorted(songs, key=lambda x: x['likelihood'], reverse=True)

def search_song_info(comments):
    """
    Extract all songs and artists from comments, validate with Serper, and compute likelihood.
    
    Args:
        comments (list): List of cleaned comments
    
    Returns:
        dict: List of all songs with likelihood scores and the most likely song
    """
    # Initialize Groq client
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # Combine comments into a single context
    comments_context = "\n".join(comments)
    
    # Step 1: Use Groq LLM to extract all potential songs and artists
    llm_prompt = (
        "You are a music expert. Below are Instagram comments guessing songs in a video:\n\n"
        f"{comments_context}\n\n"
        "Extract all mentioned song titles and artists. If no artist is mentioned, leave it blank. "
        "Include songs even if mentioned indirectly (e.g., lyrics or partial titles). "
        "Do not treat band names (e.g., 'big thief', 'coldplay') as song titles unless clearly indicated. "
        "Remove '@' from artist names (e.g., '@greenday' → 'greenday'). "
        "Output in JSON format with a field `songs` containing a list of objects with `song` and `artist` fields. "
        "Ensure the output is valid JSON."
    )
    
    songs = []
    try:
        llm_response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": llm_prompt}],
            model="llama3-70b-8192",
            response_format={"type": "json_object"}
        )
        llm_result = json.loads(llm_response.choices[0].message.content)
        songs = llm_result.get("songs", [])
    except Exception as e:
        print(f"Error with Groq LLM: {e}")
        # Attempt to recover from failed_generation if available
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                failed_text = error_data.get('error', {}).get('failed_generation', '')
                if failed_text:
                    songs = parse_failed_generation(failed_text)
            except Exception:
                pass
    
    # Step 2: Use Serper to validate songs and complete missing artists
    serper_api_key = os.getenv("SERPER_API_KEY")
    validated_songs = []
    
    for song in songs:
        song_name = song.get("song", "")
        artist = song.get("artist", "")
        
        # Clean artist name (remove '@' if still present)
        if artist.startswith('@'):
            artist = artist[1:]
        
        if song_name and not artist:
            try:
                response = requests.post(
                    "https://google.serper.dev/search",
                    headers={"X-API-KEY": serper_api_key},
                    json={"q": f"{song_name} song"}
                )
                search_results = response.json()
                if search_results.get("organic"):
                    top_result = search_results["organic"][0]
                    if " by " in top_result.get("title", ""):
                        artist = top_result["title"].split(" by ")[-1].strip()
            except Exception as e:
                print(f"Error with Serper search for {song_name}: {e}")
        
        validated_songs.append({"song": song_name, "artist": artist or "Unknown"})
    
    # Step 3: Compute likelihood scores
    validated_songs = compute_likelihood(validated_songs, comments)
    
    # Step 4: Identify most likely song
    most_likely = validated_songs[0] if validated_songs else {"song": "Unknown", "artist": "Unknown", "likelihood": 0}
    
    return {
        "all_songs": validated_songs,
        "most_likely": most_likely
    }