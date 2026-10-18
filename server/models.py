from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# A naming convention gives database constraints predictable names.
# Flask-Migrate uses these names when it creates or updates tables.
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# All models inherit database features from this shared object.
db = SQLAlchemy(metadata=metadata)

# This table connects sessions and speakers. Each row represents one
# speaker being assigned to one session.
session_speakers = db.Table(
    'session_speakers',
    db.Column(
        'session_id',
        db.Integer,
        db.ForeignKey('sessions.id'),
        primary_key=True,
    ),
    db.Column(
        'speaker_id',
        db.Integer,
        db.ForeignKey('speakers.id'),
        primary_key=True,
    ),
)


class Event(db.Model):
    __tablename__ = 'events'

    # Each model needs a primary key so every row has a unique ID.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)

    # One event can have many sessions. Deleting an event also deletes
    # its sessions because they should not exist without their event.
    sessions = db.relationship(
        'Session',
        back_populates='event',
        cascade='all, delete-orphan',
    )

    def __repr__(self):
        return f'<Event {self.id}, {self.name}, {self.location}>'


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime)

    # The foreign key stores the ID of the event that owns this session.
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    # back_populates links both sides of the Event/Session relationship.
    event = db.relationship('Event', back_populates='sessions')

    # secondary tells SQLAlchemy to use the association table so each
    # session can have many speakers and each speaker can have many sessions.
    speakers = db.relationship(
        'Speaker',
        secondary=session_speakers,
        back_populates='sessions',
    )

    def __repr__(self):
        return f'<Session {self.id}, {self.title}, {self.start_time}>'


class Speaker(db.Model):
    __tablename__ = 'speakers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # uselist=False makes this a one-to-one relationship instead of a list.
    # Deleting a speaker also deletes that speaker's bio.
    bio = db.relationship(
        'Bio',
        back_populates='speaker',
        cascade='all, delete-orphan',
        uselist=False,
    )

    # This is the other side of the many-to-many relationship with sessions.
    sessions = db.relationship(
        'Session',
        secondary=session_speakers,
        back_populates='speakers',
    )

    def __repr__(self):
        return f'<Speaker {self.id}, {self.name}>'


class Bio(db.Model):
    __tablename__ = 'bios'

    id = db.Column(db.Integer, primary_key=True)
    bio_text = db.Column(db.Text, nullable=False)

    # unique=True ensures that one speaker cannot have multiple bios.
    speaker_id = db.Column(
        db.Integer,
        db.ForeignKey('speakers.id'),
        nullable=False,
        unique=True,
    )

    # This lets a Bio object access its owner with bio.speaker.
    speaker = db.relationship('Speaker', back_populates='bio')

    def __repr__(self):
        return f'<Bio {self.id}, {self.bio_text}>'
