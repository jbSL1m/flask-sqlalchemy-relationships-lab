import pytest
from server.app import app, db
from server.models import Event, Session, Speaker, Bio
import datetime


# A fixture prepares a fresh database before each test and cleans it up
# afterward. Tests receive the ready-to-use client through test_client.
@pytest.fixture(scope="function")
def test_client():
    # TESTING makes Flask propagate errors so pytest can report them clearly.
    app.config["TESTING"] = True
    # An in-memory SQLite database is fast and disappears after the test.
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        # Build empty tables from the model definitions.
        db.create_all()

        # Add a small connected set of records for endpoint tests to query.
        event = Event(name="Tech Conference", location="New York")
        db.session.add(event)
        db.session.commit()

        session = Session(
            title="Future of AI",
            start_time=datetime.datetime(2024, 6, 1, 9, 0),
            event=event
        )
        db.session.add(session)

        speaker = Speaker(name="Jane Doe")
        db.session.add(speaker)

        bio = Bio(bio_text="Expert in AI and ML.", speaker=speaker)
        db.session.add(bio)

        session.speakers.append(speaker)

        db.session.commit()

        # yield pauses fixture setup and gives this test client to the test.
        yield app.test_client()

        # Remove the session and tables so the next test starts cleanly.
        db.session.remove()
        db.drop_all()
