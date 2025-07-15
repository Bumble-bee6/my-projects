import yt_dlp
import sys
from process_captions import process_captions
import re

def sanitize_filename(filename):
    """
    Sanitize the filename by removing or replacing invalid characters.
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    # Trim length if needed (Windows has a 255 character limit)
    return filename[:240]  # Leave room for the _captions.txt suffix

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
            video_title = sanitize_filename(info.get('title', 'Unknown_title'))
            
            # Check if English subtitles are available
            if not info.get('subtitles') or 'en' not in info['subtitles']:
                print(f"No English subtitles found for the video: {info.get('title', 'Unknown title')}")
                return None, None
            
            # Extract English subtitles
            subtitles = info['subtitles']['en']
            for fmt in subtitles:
                if fmt['ext'] == 'json3':
                    return fmt['url'], video_title
            
            return None, None
            
    except Exception as e:
        print(f"Error extracting captions: {str(e)}")
        return None, None

def main():
    if len(sys.argv) != 2:
        print("Usage: python get_youtube_captions_combined.py <youtube_url>")
        print("Example: python get_youtube_captions_combined.py https://www.youtube.com/watch?v=xxx")
        return

    url = sys.argv[1]
    print(f"Extracting and processing captions from: {url}")
    
    # Get captions URL and video title
    captions_url, video_title = get_english_captions(url)
    
    if captions_url:
        # Process the captions
        formatted_text = process_captions(captions_url)
        
        if formatted_text:
            # Save the formatted captions to subs.txt
            output_file = 'subs.txt'
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(formatted_text)
                print(f"Formatted captions saved to {output_file}")
            except Exception as e:
                print(f"Error saving captions: {str(e)}")
        else:
            print("Failed to process captions.")
    else:
        print("Failed to extract captions.")

if __name__ == "__main__":
    main()