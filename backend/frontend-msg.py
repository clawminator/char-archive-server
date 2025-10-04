#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

# sudo apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config

CACHE_SECONDS = 60

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0', 'CACHE_KEY_PREFIX': 'frontend_msg__'})
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://chub_archive_msg:geM5weix2iKiej0zej8OhfohchahhohV@h.mariadb.nb/chub_archive_msg'
db = SQLAlchemy(app)


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=False)
    msg_type = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, title, message, msg_type, active):
        self.title = title
        self.message = message
        self.msg_type = msg_type
        self.active = active


with app.app_context():
    db.create_all()
    if not Message.query.filter_by(id=1).first():
        new_message = Message('null', False, 'null', 0)
        db.session.add(new_message)
        db.session.commit()


@app.route('/msg', methods=['GET'])
@cache.cached(timeout=CACHE_SECONDS, query_string=True)
def main():
    result = Message.query.filter_by(active=True).first()
    resp = jsonify({
        "title": result.title if result else None,
        "message": result.message if result else None,
        "msg_type": result.msg_type if result else None,
    })
    resp.headers['Cache-Control'] = f'public, max-age={CACHE_SECONDS}'
    resp.headers['Access-Control-Allow-Origin'] = '*'  # For local debugging. Nginx will add the proper headers later.
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
