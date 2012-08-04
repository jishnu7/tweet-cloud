import os, urllib, simplejson
from flask import Flask, request, render_template
from collections import defaultdict

app = Flask(__name__)

@app.route('/') 
def hello():
    return render_template('home.html')
 
@app.route('/get_tweets/<handle>') 
def get_tweets(handle=""): 
    count = request.args.get('count', 10, type=int)
    exclude_replies = request.args.get('exclude_replies', True, type=bool)
    include_rts = request.args.get('include_rts', False, type=bool)

    base_url = "https://api.twitter.com/1/statuses/user_timeline.json"
    param = {
            'screen_name' : handle,
            'exclude_replies' : exclude_replies,
            'include_rts' : include_rts,
            'count' : count
            }
    print param
    url = base_url + '?' + urllib.urlencode(param)
    result = simplejson.load(urllib.urlopen(url))

    tweet_count = defaultdict(lambda:0)
    if 'errors' in result:
        return None
    else:
        for tweet in result:
            length = len(tweet['text'].split())
            tweet_count[length] += 1

    return simplejson.dumps(tweet_count)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
