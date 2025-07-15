
import re
from collections import Counter, defaultdict
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64

class DashboardAnalytics:
    def __init__(self):
        nltk.download('punkt')
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('english'))

    def extract_timestamps(self, text):
        """Extract timestamps and their corresponding text."""
        timestamp_pattern = r'\[(\d{2}:\d{2}:\d{2})\](.*?)(?=\[\d{2}:\d{2}:\d{2}\]|$)'
        timestamps = re.findall(timestamp_pattern, text, re.DOTALL)
        return [(ts[0], ts[1].strip()) for ts in timestamps]

    def calculate_word_count(self, text):
        """Calculate word count statistics."""
        # Remove timestamps
        text = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', text)
        words = word_tokenize(text)
        sentences = sent_tokenize(text)
        
        return {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'total_sentences': len(sentences),
            'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0
        }

    def calculate_speaking_speed(self, text):
        """Calculate speaking speed based on timestamps."""
        timestamps = self.extract_timestamps(text)
        if not timestamps:
            return {'avg_words_per_minute': 0, 'speaking_speed_chart': None}

        # Calculate words per minute for each segment
        speeds = []
        for i in range(len(timestamps) - 1):
            current_time = datetime.strptime(timestamps[i][0], '%H:%M:%S')
            next_time = datetime.strptime(timestamps[i+1][0], '%H:%M:%S')
            time_diff = (next_time - current_time).total_seconds() / 60  # in minutes
            
            words = len(word_tokenize(timestamps[i][1]))
            if time_diff > 0:
                speed = words / time_diff
                speeds.append(speed)

        # Generate speed chart
        plt.figure(figsize=(10, 4))
        plt.plot(range(len(speeds)), speeds)
        plt.title('Speaking Speed Over Time')
        plt.xlabel('Segment')
        plt.ylabel('Words per Minute')
        
        # Convert plot to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()

        return {
            'avg_words_per_minute': np.mean(speeds) if speeds else 0,
            'speaking_speed_chart': chart
        }

    def analyze_topic_frequency(self, text):
        """Analyze topic frequency and generate word cloud."""
        # Remove timestamps and clean text
        text = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', text)
        words = [word.lower() for word in word_tokenize(text) 
                if word.lower() not in self.stop_words and word.isalnum()]
        
        # Calculate word frequencies
        word_freq = Counter(words)
        
        # Generate word cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
        
        # Convert word cloud to base64 string
        buf = io.BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.savefig(buf, format='png')
        buf.seek(0)
        wordcloud_img = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()

        return {
            'top_topics': dict(word_freq.most_common(10)),
            'wordcloud': wordcloud_img
        }

    def generate_engagement_heatmap(self, text, comments=None, likes=None):
        """Generate engagement heatmap based on content and optional engagement metrics."""
        timestamps = self.extract_timestamps(text)
        if not timestamps:
            return {'heatmap': None}

        # Calculate engagement scores for each segment
        engagement_scores = []
        for timestamp, content in timestamps:
            # Basic engagement score based on content length and sentiment
            sentiment = TextBlob(content).sentiment.polarity
            length_score = len(word_tokenize(content)) / 100  # Normalize length
            engagement_score = (sentiment + 1) * length_score  # Combine factors
            engagement_scores.append(engagement_score)

        # Generate heatmap
        plt.figure(figsize=(10, 4))
        plt.imshow([engagement_scores], aspect='auto', cmap='YlOrRd')
        plt.colorbar(label='Engagement Score')
        plt.title('Content Engagement Heatmap')
        plt.xlabel('Video Timeline')
        plt.yticks([])
        
        # Convert heatmap to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        heatmap = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()

        return {
            'heatmap': heatmap,
            'engagement_scores': engagement_scores
        }

    def get_dashboard_data(self, text, comments=None, likes=None):
        """Get all dashboard analytics data."""
        return {
            'word_count': self.calculate_word_count(text),
            'speaking_speed': self.calculate_speaking_speed(text),
            'topic_frequency': self.analyze_topic_frequency(text),
            'engagement': self.generate_engagement_heatmap(text, comments, likes)
        } 