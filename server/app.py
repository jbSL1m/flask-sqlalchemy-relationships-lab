#!/usr/bin/env python3

from flask import Flask, jsonify
from flask_migrate import Migrate

from models import db, Event, Session, Speaker, Bio

# Create the Flask application and configure its SQLite database.
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Pretty-print JSON responses so they are easier to read while learning.
app.json.compact = False

# Flask-Migrate tracks database structure changes, while init_app connects
# the shared db object from models.py to this Flask application.
migrate = Migrate(app, db)
db.init_app(app)


@app.route('/events')
def get_events():
    # Convert every Event model into a plain dictionary that Flask can
    # serialize as JSON.
    events = [
        {
            'id': event.id,
            'name': event.name,
            'location': event.location,
        }
        for event in Event.query.all()
    ]
    return jsonify(events), 200


@app.route('/events/<int:id>/sessions')
def get_event_sessions(id):
    # db.session.get looks up one row by its primary key.
    event = db.session.get(Event, id)
    if event is None:
        return jsonify({'error': 'Event not found'}), 404

    # The event.sessions relationship supplies only sessions for this event.
    sessions = [
        {
            'id': session.id,
            'title': session.title,
            # JSON has no DateTime type, so convert the value to text.
            'start_time': (
                session.start_time.isoformat()
                if session.start_time is not None
                else None
            ),
        }
        for session in event.sessions
    ]
    return jsonify(sessions), 200


@app.route('/speakers')
def get_speakers():
    # Return a short summary of every speaker.
    speakers = [
        {
            'id': speaker.id,
            'name': speaker.name,
        }
        for speaker in Speaker.query.all()
    ]
    return jsonify(speakers), 200


@app.route('/speakers/<int:id>')
def get_speaker(id):
    speaker = db.session.get(Speaker, id)
    if speaker is None:
        return jsonify({'error': 'Speaker not found'}), 404

    # A speaker is allowed to exist without a related Bio row.
    return jsonify({
        'id': speaker.id,
        'name': speaker.name,
        'bio_text': (
            speaker.bio.bio_text
            if speaker.bio is not None
            else 'No bio available'
        ),
    }), 200


@app.route('/sessions/<int:id>/speakers')
def get_session_speakers(id):
    session = db.session.get(Session, id)
    if session is None:
        return jsonify({'error': 'Session not found'}), 404

    # session.speakers follows the many-to-many relationship defined
    # through the session_speakers association table.
    speakers = [
        {
            'id': speaker.id,
            'name': speaker.name,
            'bio_text': (
                speaker.bio.bio_text
                if speaker.bio is not None
                else 'No bio available'
            ),
        }
        for speaker in session.speakers
    ]
    return jsonify(speakers), 200


if __name__ == '__main__':
    # This block runs only when app.py is started directly.
    app.run(port=5555, debug=True)