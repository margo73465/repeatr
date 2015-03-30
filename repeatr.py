# all the imports
import sqlite3
import json
import requests
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

# __name__ is the name of the current module
# from_object takes all of the upper case varibles from the object
# set up instance folder to keep YouTube API key secret
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# sets up connection with the database (specified in config)
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# can be used to initialize the database using the schema provided in
# schema.sql. Not called anywhere (since we don't want to initialize
# the database every time), intended to be usef form the console.
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# creates a connection with the database before each request
@app.before_request
def before_request():
    g.db = connect_db()

# destroys connection with the database after request
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# users attempting to reach the homepage are redirected to a default video
@app.route('/')
def home():
    return redirect("/watch?v=Dsg8JccRZCw", code=302)

# primary route - sends current video id and data on the top 10 videos to the 
# show_video template
@app.route('/watch', methods=['GET'])
def show_video():
    # get video ID from get request query string
    video_id = str(request.args.get('v'))

    # grab top 10 most looped videos from database and put relevant info into 
    # a dictionary
    cursor = g.db.execute('SELECT * from videos ORDER BY play_count DESC LIMIT 10')
    videos = [dict(video_id=row[0], title=row[1], description=row[2], 
        thumbnail_url=row[3], play_count=row[4]) for row in cursor.fetchall()]
    
    return render_template('show_video.html', video_id=video_id, top_10=videos)

# utility route, only accepts post requests (usually from client side AJAX call sent
# every time a video is played fully)
# - for new videos a request is made to the YouTube data API for additional information
#   (title, description, thumbnail_url) that is then stored in the database
# - videos that are already in the database simply have their play_count incremented by 1
@app.route('/update_database/', methods=['POST'])
def update():

    data = json.loads(request.data)
    video_id = data['video_id']
    cursor = g.db.execute('SELECT * FROM videos WHERE video_id = ?', [video_id])
    data = cursor.fetchone()

    if (data is None):
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/videos?part=snippet&alt=json&id=" + 
            video_id + "&key=" + app.config['YOUTUBE_API_KEY'])
        snippet = r.json().items()[0][1][0]['snippet']
        title = snippet['title']
        description = snippet['description']
        thumbnail_url = snippet['thumbnails']['default']['url']

        g.db.execute('INSERT INTO videos (video_id, title, description, \
            thumbnail_url, play_count) VALUES (?, ?, ?, ?, ?)', 
            [video_id, title, description, thumbnail_url, 1])

    else: 
        g.db.execute('UPDATE videos SET play_count = play_count + 1 WHERE video_id = ?', [video_id])

    g.db.commit()

    return "HTTP_OK", 200


if __name__ == '__main__':
    app.run()
