import os, urllib, simplejson
from flask import Flask, request, render_template, Response
from collections import defaultdict

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('home.html')

@app.route('/get_tweets/<handle>')
def get_tweets(handle=""):
    count = request.args.get('count', 1000, type=int)
    replies = request.args.get('replies', False, type=int)
    include_rts = request.args.get('include_rts', False, type=int)

    base_url = "https://api.twitter.com/1/statuses/user_timeline.json"
    param = {
            'screen_name' : handle,
            'exclude_replies' : not replies,
            'include_rts' : include_rts,
            'count' : count
            }
    print param
    
    url = base_url + '?' + urllib.urlencode(param)
    result = simplejson.load(urllib.urlopen(url))

    type_value = request.args.get('type', 'word_count', type=str)
    data = values(type_value, result)
    json = simplejson.dumps(data)
    resp = Response(json, status=200, mimetype='application/json')
    return resp

def values(option, data):
    return {
    'word_count': word_count,
    'words': words,
    'hashtags': hashtags
    }.get(option, word_count)(data)

def word_count(data):
    tweet_count = defaultdict(lambda:0)
    if 'errors' in data:
        return None
    else:
        for tweet in data:
            length = len(tweet['text'].split())
            tweet_count[length] += 1
    print dict(tweet_count)
    return tweet_count

def words(data):
    tweets = defaultdict(lambda:0)
    if 'errors' in data:
        return None
    else:
        for tweet in data:
            # TODO: Bad method. Need to clean words. Improve later
            text = tweet['text'].replace(".", " ").replace(",", " ").replace("-", " ")
            words = text.split()
            for word in words:
                tweets[word] += 1
    # We dont need words with frequency 1
    tweets = {key: value for key, value in tweets.items() if value != 1}
    print dict(tweets)
    return tweets

def hashtags(data):
    tweets = defaultdict(lambda:0)
    if 'errors' in data:
        return None
    else:
        for tweet in data:
            # TODO: Bad method. Need to clean hashtags. Improve later
            text = tweet['text'].replace(".", " ").replace(",", " ").replace("-", " ")
            words = text.split()
            for word in words:
                if word.startswith("#"):
                    tweets[word] += 1
    print dict(tweets)
    return tweets 

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
