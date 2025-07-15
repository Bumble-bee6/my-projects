import yt_dlp
import sys

OUTPUT_FILE = 'english_captions.txt'  # Predefined output file

def get_english_captions(url):
    """
    Extract English captions from a YouTube video.
    
    Args:
        url (str): YouTube video URL
    
    Returns:
        str: URL to the captions data, or None if not available
    """
    ydl_opts = {
        'writesubtitles': True,
        'subtitleslangs': ['en'],
        'skip_download': True,
        'quiet': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info
            info = ydl.extract_info(url, download=False)
            
            # Check if English subtitles are available
            if not info.get('subtitles') or 'en' not in info['subtitles']:
                print(f"No English subtitles found for the video: {info.get('title', 'Unknown title')}")
                return None
            
            # Extract English subtitles
            subtitles = info['subtitles']['en']
            for fmt in subtitles:
                if fmt['ext'] == 'json3':
                    return fmt['url']
            
            return None
            
    except Exception as e:
        print(f"Error extracting captions: {str(e)}")
        return None

def save_captions_to_file(captions):
    """Save captions to the predefined output file."""
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(captions)
        print(f"Captions saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving captions: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python youtube_caption_extractor.py <youtube_url>")
        print("Example: python youtube_caption_extractor.py https://www.youtube.com/watch?v=xxx")
        return

    url = sys.argv[1]
    print(f"Extracting English captions from: {url}")
    captions = get_english_captions(url)
    
    if captions:
        save_captions_to_file(captions)

if __name__ == "__main__":
    main()