import json
from youtube_transcript_api import YouTubeTranscriptApi
from flask import Flask, request, jsonify
from nltk import word_tokenize, pos_tag
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/test')
def test():
    return 'test'

# Return a blurred version of the title
@app.route('/get_blured_title', methods=['GET'])
def get_blured_title():
    blur_tags = ['NN', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'CD', 'EM']
    video_title = request.args.get('videoTitle')
    words = word_tokenize(video_title)
    tagged_words = pos_tag(words)
    blurred = []
    for word, tag in tagged_words:
        if tag in blur_tags:
            blurred.append('<span class="blur-text">[BLUR]</span>')
        elif len(word) == 1 or word == "n't":
            pass
        else:
            blurred.append(word)
    topic = ' '.join(blurred)
    return jsonify({'videoTitle': video_title, 'topic': topic, 'tagged_words': tagged_words})

# Return the name of the media discussed in the video (or None)
@app.route('/get_video_topic', methods=['GET'])
def get_video_topic():
    video_title = request.args.get('videoTitle')
    video_id = request.args.get('videoID')
    transcript = get_youtube_video_transcript(video_id)
    
    if isinstance(transcript, dict) and 'error' in transcript:
        return jsonify({'error': transcript['error']}), 500
    
    media = findMedia(transcript)
    confidence_value = set(media.split()).issubset(set(video_title.split()))
    return jsonify({'media': media, 'bool':confidence_value})

# Return a boolean isSpoiler
@app.route('/is_video_spoiler', methods=['GET'])
def is_video_spoiler():
    return jsonify({"isSpoiler": True})

# GET VIDEO TOPIC FUNCTIONS BELOW
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

def get_youtube_video_transcript(video_id):
    try:
        transcript = ""
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        for elt in transcript_list:
            transcript += elt['text'] + ' '
        return transcript
    except Exception as e:
        return {"error": str(e)}

def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_text = [word for word in word_tokens if word.lower() not in stop_words]
    clean_transcript = ""
    for w in filtered_text:
        if not ("'" in w) and len(w) > 1:
            clean_transcript += w + " "
    return clean_transcript

def count_words(transcript):
    word_counts = Counter(transcript.split())
    return word_counts

def count_phrases(transcript, phrase_length=2):
    words = transcript.split()
    phrases = [" ".join(words[i:i+phrase_length]) for i in range(len(words)-phrase_length+1)]
    phrase_counts = Counter(phrases)
    return phrase_counts

def findMedia(transcript):
    clean_transcript = remove_stopwords(transcript)
    word_counts = count_words(clean_transcript)
    two_word_phrases = count_phrases(clean_transcript, 2)
    three_word_phrases = count_phrases(clean_transcript, 3)
    oneW = word_counts.most_common(1)[0]
    twoW = two_word_phrases.most_common(1)[0]
    threeW = three_word_phrases.most_common(1)[0]
    scores = [oneW[1], twoW[1]*5, threeW[1]*8]
    max_index = scores.index(max(scores))
    if max_index == 0:
        max_word = oneW[0]
    elif max_index == 1:
        max_word = twoW[0]
    else:
        max_word = threeW[0]
    return max_word

if __name__ == '__main__':
    app.run()
