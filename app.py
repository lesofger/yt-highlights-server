from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from googleapiclient.discovery import build # type: ignore
import re

app = Flask(__name__)

def get_youtube_transcript(video_url):
    try:
        # Extract video ID from URL
        video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", video_url).group(1)
        print("Video ID:", video_id)

        proxies = {
            'http': 'http://195.158.8.123:3128',
            'https': 'http://195.158.8.123:3128'
        }
        
        # Fetch transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'], proxies=proxies )
        print("Transcript1:", transcript)
        
        return transcript
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
            part='statistics, snippet',
            id=video_id
        )
        response = request.execute()
        
        # Extract metrics
        if response['items']:
            item = response['items'][0]
            stats = item['statistics']
            snippet = item['snippet']
            metrics = {
                'title': snippet.get('title', 'N/A'),
                'view_count': stats.get('viewCount', 'N/A'),
                'like_count': stats.get('likeCount', 'N/A'),
                'comment_count': stats.get('commentCount', 'N/A'),
                # 'dislike_count': stats.get('dislikeCount', 'N/A')  # Only available for your own videos with OAuth
            }
            print("Metrics:", metrics)

            # Fetch top 20 comments (sorted by relevance or time)
            comment_request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=20,
                order='relevance',  # You can use 'time' instead to get most recent comments
                textFormat='plainText'
            )
            comment_response = comment_request.execute()

            # Extract comment texts
            comments = []
            for item in comment_response.get('items', []):
                top_comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(top_comment)
            
            metrics['top_comments'] = comments
            return metrics
        else:
            return "No metrics found for this video."
    except Exception as e:
        return f"Error fetching metrics: {str(e)}"
    
def get_youtube_data(video_url, api_key):
    # Fetch both transcript and metrics
    transcript = get_youtube_transcript(video_url)
    metrics = get_youtube_metrics(video_url, api_key)
    
    return {
        'transcript': transcript,
        'metrics': metrics
    }


@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/api/youtube-transcript', methods=['POST'])
def youtube_transcript():
    api_key = "AIzaSyCnZqOuzIc-MwTxwgS4lFNtWri6wWPXofw"
    data = request.get_json()
    video_url = data.get('video_url', '')

    if not video_url:
        return jsonify(error="Missing 'video_url' in request."), 400

    youtube_data = get_youtube_data(video_url, api_key)
    return jsonify(youtube_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9888)
