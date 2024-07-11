from youtube_transcript_api import YouTubeTranscriptApi
from flask import Flask, request, jsonify
from nltk import word_tokenize, pos_tag
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello World'

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

if __name__ == '__main__':
    app.run()
