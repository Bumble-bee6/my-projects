# YouTube Transcript Summarizer

A web application that extracts transcripts from YouTube videos and generates concise summaries using AI. The application provides different summary lengths and allows you to view both the full transcript and the generated summary.

## Features

- Extract English captions from YouTube videos
- Generate AI-powered summaries with three different length options:
  - Brief: Key points only
  - Standard: Balanced overview
  - Detailed: In-depth coverage
- View full video transcript with timestamps
- Dark/Light theme support
- Copy and save results
- View history of processed videos

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- Web browser (Chrome, Firefox, Safari, or Edge)

## Installation

1. Clone this repository or download the source code:
```bash
git clone <repository-url>
cd youtube_captions
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

This will install the following dependencies:
- Flask: Web framework
- Flask-CORS: Cross-Origin Resource Sharing support
- transformers: For AI-powered text summarization
- torch: Required for transformers
- yt-dlp: YouTube video and caption extraction
- requests: HTTP requests handling

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Paste a YouTube video URL into the input field
2. Select your preferred summary length:
   - Brief: For quick overview
   - Standard: Balanced summary
   - Detailed: Comprehensive summary
3. Click "Generate Summary" to process the video
4. Switch between tabs to view:
   - Summary: AI-generated summary of the content
   - Transcript: Full transcript with timestamps
   - History: Previously processed videos

## Features Details

### Summary Generation
The application uses the BART model (facebook/bart-large-cnn) to generate summaries. The summary length options correspond to different configurations:
- Brief: 60-200 words
- Standard: 100-300 words
- Detailed: 200-500 words

### Transcript Processing
- Automatically extracts English captions from YouTube videos
- Preserves timestamp information
- Handles automatic and manual captions

### User Interface
- Responsive design that works on both desktop and mobile
- Dark/Light theme toggle
- Loading indicators for better user experience
- Copy and Save functionality for both summaries and transcripts

## Limitations

- Only works with YouTube videos that have English captions available
- Requires an active internet connection
- Processing time may vary depending on video length and summary type

## Error Handling

The application handles various error cases:
- Invalid YouTube URLs
- Videos without available captions
- Network connectivity issues
- Processing failures

## Technical Details

### Backend
- Flask server handling API requests
- yt-dlp for YouTube caption extraction
- Transformers library for text summarization

### Frontend
- Pure HTML, CSS, and JavaScript
- No external frontend frameworks required
- Responsive design using CSS Grid and Flexbox

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Acknowledgments

- BART model by Facebook AI
- yt-dlp project
- Hugging Face Transformers library