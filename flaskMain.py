from flask import Flask, request, jsonify
from nltk import word_tokenize, pos_tag, RegexpParser
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/test')
def test():
    return 'test'

@app.route('/get_video_topic', methods=['GET'])
def get_video_topic():
    blur_tags = ['NN', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'CD','EM']
    video_title = request.args.get('videoTitle')
    print(video_title)
    words = word_tokenize(video_title)
    tagged_words = pos_tag(words)
    blurred = []
    for word, tag in tagged_words:
        if tag in blur_tags: blurred.append('[BLUR]')
        elif len(tag) == 1 : pass
        else: blurred.append(word)
    topic = ' '.join(blurred)
    return jsonify({'videoTitle': video_title, 'topic': topic})

if __name__ == '__main__':
    app.run(debug=True)