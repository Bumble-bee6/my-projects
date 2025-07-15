import json
import requests
from datetime import datetime

def format_timestamp(milliseconds):
    """Convert milliseconds to readable timestamp format HH:MM:SS"""
    seconds = int(milliseconds / 1000)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def process_captions(json_url):
    """
    Process the JSON3 format captions and convert to readable text format.
    
    Args:
        json_url (str): URL to the JSON3 captions data
    
    Returns:
        str: Formatted captions text
    """
    try:
        # Fetch the JSON data from the URL
        response = requests.get(json_url)
        response.raise_for_status()
        caption_data = response.json()
        
        # Process events (actual captions)
        formatted_captions = []
        
        if 'events' in caption_data:
            for event in caption_data['events']:
                if 'segs' in event and event.get('segs'):
                    # Get the start time
                    start_time = format_timestamp(event.get('tStartMs', 0))
                    
                    # Combine all segments into one line
                    text = ' '.join(
                        seg.get('utf8', '') for seg in event['segs']
                        if seg.get('utf8')
                    ).strip()
                    
                    if text:  # Only add non-empty captions
                        formatted_captions.append(f"[{start_time}] {text}")
        
        return '\n\n'.join(formatted_captions)
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching captions: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

def main():
    # Read the JSON URL from the file created by youtube_caption_extractor.py
    try:
        with open('english_captions.txt', 'r', encoding='utf-8') as f:
            json_url = f.read().strip()
        
        # Process the captions
        formatted_text = process_captions(json_url)
        
        if formatted_text:
            # Save the formatted captions
            output_file = 'formatted_captions.txt'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(formatted_text)
            print(f"Formatted captions saved to {output_file}")
        else:
            print("Failed to process captions.")
            
    except FileNotFoundError:
        print("Error: english_captions.txt not found. Please run youtube_caption_extractor.py first.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()