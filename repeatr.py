# all the imports
import sqlite3
import json
import requests
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

# __name__ is the name of the current module
# from_object takes all of the upper case varibles from the object
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# @app.route('/')
# def get_top_10():
# 	top_10 = g.db.execute('SELECT * from videos ORDER BY play_count LIMIT 10')
# 	videos = []
# 	for row in top_10.fetchall():
# 		videos.push({title: row[1], link: row[2], image_link: row[3], description: row[3], play_count: row[4]})
# 	return render_template('show_video.html', videos=videos)

@app.route('/watch', methods=['GET'])
def show_video():
    video_id = str(request.args.get('v'))

    cur = g.db.execute('SELECT title, play_count from videos ORDER BY play_count LIMIT 10')
    videos = [dict(title=row[0], play_count=row[1]) for row in cur.fetchall()]
    
    return render_template('show_video.html', video_id=video_id, top_10=videos)


@app.route('/update_database/', methods=['POST'])
def update():

    data = json.loads(request.data)
    video_id = data['video_id']
    cursor = g.db.execute('SELECT * FROM videos WHERE video_id = ?', [video_id])
    print cursor
    data = cursor.fetchone()
    print data

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

    # cur = g.db.execute('SELECT title, play_count from videos ORDER BY play_count LIMIT 10')
    # videos = [dict(title=row[0], play_count=row[1]) for row in cur.fetchall()]

    return "post successful... I think"
    # return render_template('show_video.html', video_id=video_id, top_10=videos)


if __name__ == '__main__':
    app.run()
