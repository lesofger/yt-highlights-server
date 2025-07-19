from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from googleapiclient.discovery import build
import re

app = Flask(__name__)

def get_youtube_transcript(video_url):
    try:
        # Extract video ID from URL
        video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", video_url).group(1)
        print("Video ID:", video_id)
        
        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        print("Transcript1:", transcript)
        formatter = TextFormatter()
        formatted_transcript = formatter.format_transcript(transcript)
        print("Transcript2:", formatted_transcript)
        
        return formatted_transcript
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

def get_youtube_metrics(video_url, api_key):
    try:
        # Extract video ID from URL
        video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", video_url).group(1)
        
        # Initialize YouTube API client
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Fetch video details
        request = youtube.videos().list(
            part='statistics',
            id=video_id
        )
        response = request.execute()
        
        # Extract metrics
        if response['items']:
            stats = response['items'][0]['statistics']
            metrics = {
                'view_count': stats.get('viewCount', 'N/A'),
                'like_count': stats.get('likeCount', 'N/A'),
                'comment_count': stats.get('commentCount', 'N/A'),
                # 'dislike_count': stats.get('dislikeCount', 'N/A')  # Only available for your own videos with OAuth
            }
            print("Metrics:", metrics)
            return metrics
        else:
            return "No metrics found for this video."
    except Exception as e:
        return f"Error fetching metrics: {str(e)}"


@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/api/greet', methods=['POST'])
def greet():
    data = request.get_json()
    name = data.get('name', 'Guest')
    return jsonify(message=f"Hello, {name}!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9888)
