from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Show(db.Model):
    # Table name
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id', ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)
    venue = db.relationship('Venue', back_populates='artists_show',
                            lazy=True, cascade='all, delete', passive_deletes=True)
    artist = db.relationship('Artist', back_populates='venues_show',
                             lazy=True, cascade='all, delete', passive_deletes=True)


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=True)

    artists_show = db.relationship(
        "Show", back_populates="venue", cascade='all, delete')

    def __repr__(self):
        return f"\n<Venue id: {self.id} name: {self.name}>"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    phone = db.Column(db.String(15), nullable=True, unique=True)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(500), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(300), nullable=True)

    venues_show = db.relationship(
        "Show", back_populates="artist", cascade='all, delete')

    def __repr__(self):
        return f"\n<Artist id: {self.id} name: {self.name}>"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
