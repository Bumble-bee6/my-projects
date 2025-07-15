from transformers import pipeline
import re
import sys
from typing import List, Literal, Dict, TypedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
import torch
from tqdm import tqdm

class SummaryParams(TypedDict):
    max_length: int
    min_length: int
    chunk_size: int
    overlap_size: int  # New parameter for chunk overlap

SummaryLevel = Literal['brief', 'standard', 'detailed']

# Updated configuration for different summary levels
SUMMARY_CONFIGS: Dict[SummaryLevel, SummaryParams] = {
    'brief': {
        'max_length': 200,
        'min_length': 60,
        'chunk_size': 1000,
        'overlap_size': 100
    },
    'standard': {
        'max_length': 300,
        'min_length': 100,
        'chunk_size': 800,
        'overlap_size': 150
    },
    'detailed': {
        'max_length': 500,
        'min_length': 200,
        'chunk_size': 600,
        'overlap_size': 200
    }
}

def clean_transcript(text: str) -> str:
    """Remove timestamps and clean up the transcript text."""
    # Remove timestamps [00:00:00]
    cleaned = re.sub(r'\[\d{2}:\d{2}:\d{2}\]\s*', '', text)
    # Remove multiple newlines and spaces
    cleaned = re.sub(r'\n+', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def chunk_text(text: str, chunk_size: int, overlap_size: int) -> List[str]:
    """Split text into overlapping chunks while preserving sentence boundaries."""
    # Split into sentences (improved sentence splitting)
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    chunks = []
    current_chunk = []
    current_length = 0
    
    for i, sentence in enumerate(sentences):
        # Count words in the sentence
        sentence_length = len(sentence.split())
        
        if current_length + sentence_length > chunk_size and current_chunk:
            # Join the current chunk and add to chunks
            chunks.append('. '.join(current_chunk) + '.')
            
            # Start new chunk with overlap
            overlap_words = []
            overlap_length = 0
            for prev_sentence in reversed(current_chunk):
                prev_length = len(prev_sentence.split())
                if overlap_length + prev_length <= overlap_size:
                    overlap_words.insert(0, prev_sentence)
                    overlap_length += prev_length
                else:
                    break
            
            current_chunk = overlap_words + [sentence]
            current_length = overlap_length + sentence_length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')
    
    return chunks

def summarize_chunk(summarizer, text: str, max_length: int, min_length: int) -> str:
    """Summarize a single chunk of text."""
    try:
        # Add safety check for empty or very short text
        if not text.strip() or len(text.split()) < min_length:
            return text
            
        result = summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            truncation=True
        )
        return result[0]['summary_text']
    except Exception as e:
        print(f"Warning: Error summarizing chunk: {str(e)}")
        # Return a portion of the original text if summarization fails
        words = text.split()
        return ' '.join(words[:min_length])

def combine_summaries(summaries: List[str], max_length: int) -> str:
    """Combine multiple summaries into a coherent final summary."""
    combined = ' '.join(summaries)
    
    # If the combined summary is too long, summarize it again
    if len(combined.split()) > max_length:
        try:
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            result = summarizer(
                combined,
                max_length=max_length,
                min_length=max_length // 2,
                do_sample=False,
                truncation=True
            )
            return result[0]['summary_text']
        except Exception as e:
            print(f"Warning: Error combining summaries: {str(e)}")
            # Return a truncated version if summarization fails
            words = combined.split()
            return ' '.join(words[:max_length])
    
    return combined

def summarize_text(text: str, level: SummaryLevel = 'standard') -> str:
    """Generate a summary using the BART model with specified level."""
    try:
        # Get configuration for the specified level
        config = SUMMARY_CONFIGS[level]
        
        # Initialize the summarization pipeline
        print(f"Loading summarization model for {level} summary...")
        device = 0 if torch.cuda.is_available() else -1
        summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=device
        )
        
        # Clean the text
        cleaned_text = clean_transcript(text)
        
        # Split into chunks if text is too long
        chunks = chunk_text(cleaned_text, config['chunk_size'], config['overlap_size'])
        
        if not chunks:
            raise ValueError("No valid text chunks to summarize")
        
        print(f"Generating {level} summary ({len(chunks)} chunks)...")
        summaries = []
        
        # Process chunks in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=min(4, len(chunks))) as executor:
            # Create a progress bar
            with tqdm(total=len(chunks), desc="Processing chunks") as pbar:
                # Submit all tasks
                future_to_chunk = {
                    executor.submit(
                        summarize_chunk,
                        summarizer,
                        chunk,
                        config['max_length'],
                        config['min_length']
                    ): i for i, chunk in enumerate(chunks)
                }
                
                # Process completed tasks as they finish
                for future in as_completed(future_to_chunk):
                    chunk_index = future_to_chunk[future]
                    try:
                        summary = future.result()
                        if summary:
                            summaries.append(summary)
                    except Exception as e:
                        print(f"Error processing chunk {chunk_index}: {str(e)}")
                    pbar.update(1)
        
        if not summaries:
            raise ValueError("No summaries generated")
        
        # Combine summaries
        final_summary = combine_summaries(summaries, config['max_length'])
        
        # Clean up the final summary
        final_summary = re.sub(r'\s+', ' ', final_summary).strip()
        return final_summary
        
    except Exception as e:
        print(f"Error during summarization: {str(e)}")
        raise

def main():
    try:
        # Check if summary level is provided as argument
        level: SummaryLevel = 'standard'  # Default level
        if len(sys.argv) > 1 and sys.argv[1] in SUMMARY_CONFIGS:
            level = sys.argv[1]  # type: ignore
        
        # Read the transcript
        print(f"Reading transcript from subs.txt for {level} summary...")
        with open('subs.txt', 'r', encoding='utf-8') as file:
            transcript = file.read()
        
        if not transcript.strip():
            raise ValueError("The transcript file is empty")
        
        # Generate summary
        summary = summarize_text(transcript, level)
        
        # Save and display the summary
        print(f"\n{level.upper()} SUMMARY:")
        print("-" * 80)
        print(summary)
        print("-" * 80)
        
        # Save to file with level indication
        output_file = f'summary_{level}.txt'
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(summary)
        print(f"\nSummary saved to {output_file}")
        
    except FileNotFoundError:
        print("Error: Could not find subs.txt file.")
        print("Make sure to run the caption extractor first to generate subs.txt")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()