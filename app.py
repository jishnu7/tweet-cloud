'''
    Tweet Cloud
    Copyright (C) 2012 jishnu7@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, urllib, simplejson
from flask import Flask, request, render_template, Response
from collections import defaultdict

STRINGS= [',', '.', '-', '"']

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('home.html')

@app.route('/get_tweets/<handle>')
def get_tweets(handle=""):
    max_count = request.args.get('count', 1000, type=int)
    replies = request.args.get('replies', False, type=int)
    include_rts = request.args.get('include_rts', False, type=int)

    base_url = "https://api.twitter.com/1/statuses/user_timeline.json"
    param = {
            'screen_name' : handle,
            'exclude_replies' : not replies,
            'include_rts' : include_rts,
            'count': 200,
            'trim_user': 'true'
            }
    print param
    
    result = []
    length = 0
    while length < max_count:
        if length != 0:
            param['max_id'] = result[-1]['id'] - 1
            print param['max_id']

        url = base_url + '?' + urllib.urlencode(param)
        temp = simplejson.load(urllib.urlopen(url))
        if len(temp) == 0:
            break

        remaining = max_count - length
        result.extend(temp[:remaining])
        length = len(result)
        print "Length---->",length

    type_value = request.args.get('type', 'word_count', type=str)
    data = values(type_value, result)
    print dict(data)

    json = simplejson.dumps({'data': data, 'count': length})
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
            text = tweet['text']
            # TODO: Improve later
            for ch in STRINGS:
                text = text.replace(ch, ' ')
            length = len(text.split())
            tweet_count[length] += 1
    return tweet_count

def words(data):
    tweets = defaultdict(lambda:0)
    if 'errors' in data:
        return None
    else:
        for tweet in data:
            # TODO: Improve later
            text = tweet['text']
            for ch in STRINGS:
                text = text.replace(ch, ' ')
            words = text.split()
            for word in words:
                if not word.startswith("#"):
                    tweets[word] += 1
    # We dont need words with frequency < 3
    tweets = {key: value for key, value in tweets.items() if value > 3}
    return tweets

def hashtags(data):
    tweets = defaultdict(lambda:0)
    if 'errors' in data:
        return None
    else:
        for tweet in data:
            # TODO: Improve later
            text = tweet['text']
            for ch in STRINGS:
                text = text.replace(ch, ' ')
            words = text.split()
            for word in words:
                if word.startswith("#"):
                    tweets[word] += 1
    # We dont need words with frequency 1
    tweets = {key: value for key, value in tweets.items() if value != 1}
    return tweets 

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
