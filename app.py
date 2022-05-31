#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import datetime
from enum import unique
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import os
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

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
    start_time = db.Column(db.DateTime, nullable=False)
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
        return f"\n<Artist id: {self.id} name: {self.name} location_id: {self.location_id}>"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    # data = [
    #     {
    #         "city": "San Francisco",
    #         "state": "CA",
    #         "venues": [
    #             {
    #                 "id": 1,
    #                 "name": "The Musical Hop",
    #                 "num_upcoming_shows": 0,
    #             },
    #             {
    #                 "id": 3,
    #                 "name": "Park Square Live Music & Coffee",
    #                 "num_upcoming_shows": 1,
    #             }
    #         ]
    #     },
    #     {
    #         "city": "New York",
    #         "state": "NY",
    #         "venues": [
    #             {
    #                 "id": 2,
    #                 "name": "The Dueling Pianos Bar",
    #                 "num_upcoming_shows": 0,
    #             }
    #         ]
    #     }
    # ]
    try:
        locations = Venue.query.distinct(Venue.city, Venue.state).all()
        data = []
        for venue in locations:
            object = {}
            object['city'] = venue.city
            object['state'] = venue.state

            venues = []

            venue_data = Venue.query.filter(
                Venue.state == venue.state, Venue.city == venue.city).all()

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            for this_venue in venue_data:
                current_venue = {}
                current_venue['id'] = this_venue.id
                current_venue['name'] = this_venue.name
                current_venue['num_upcoming_shows'] = Show.query.filter(
                    db.and_(Show.start_time > current_time, Show.venue_id == this_venue.id)).count()
                venues.append(current_venue)
            object['venues'] = venues
            data.append(object)
    except:
        flash(
            f"Sorry due, to an issue on our end, we are unable to display the venues page.", category="error")
        abort(500)
    finally:
        return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    # print(request.form['search_term'].lower(), request.form.get('search_term', ''))
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    try:
        data = Venue.query.filter(db.func.lower(Venue.name).like(
            f"%{request.form['search_term'].lower()}%")).order_by('name').all()
        # print(request.form['search_term'].lower(), request.form.get('search_term', ''))
        venues = []

        for venue in data:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            info = {}
            info['id'] = venue.id
            info['name'] = venue.name
            info['num_upcoming_shows'] = Show.query.filter(
                db.and_(Show.start_time > current_time, Show.venue_id == venue.id)).count()
            venues.append(info)
        response = {
            "count": len(data),
            "data": venues
        }
    except:
        flash(f"Sorry, an error occurred while fetching your search results.", category="error")
        abort(500)
    finally:
        return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # data1 = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #         "artist_id": 4,
    #         "artist_name": "Guns N Petals",
    #         "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #         "artist_id": 5,
    #         "artist_name": "Matt Quevedo",
    #         "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] ==
    #             venue_id, [data1, data2, data3]))[0]
    try:
        data = {}
        isFound = False
        venue_data = Venue.query.filter(Venue.id == venue_id).first()
        if venue_data:
            isFound = True
            data = {}
            data['id'] = venue_data.id
            data['name'] = venue_data.name
            data['genres'] = venue_data.genres
            data['address'] = venue_data.address
            data['city'] = venue_data.city
            data['state'] = venue_data.state
            data['phone'] = venue_data.phone
            data['website'] = venue_data.website
            data['facebook_link'] = venue_data.facebook_link
            data['seeking_talent'] = venue_data.seeking_talent
            data['image_link'] = venue_data.image_link
            past_shows = []
            upcoming_shows = []
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            past = Show.query.filter(
                db.and_(Show.start_time < current_time, Show.venue_id == venue_id)).all()
            for show in past:
                past_show = {}
                past_show['artist_id'] = show.artist_id
                past_show['artist_name'] = Artist.query.filter(
                    Artist.id == show.artist_id).first().name
                past_show['artist_image_link'] = Artist.query.filter(
                    Artist.id == show.artist_id).first().image_link
                past_show['start_time'] = str(show.start_time)
                past_shows.append(past_show)

            upcoming = Show.query.filter(
                db.and_(Show.start_time > current_time, Show.venue_id == venue_id)).all()
            for show in upcoming:
                upcoming_show = {}
                upcoming_show['artist_id'] = show.artist_id
                upcoming_show['artist_name'] = Artist.query.filter(
                    Artist.id == show.artist_id).first().name
                upcoming_show['artist_image_link'] = Artist.query.filter(
                    Artist.id == show.artist_id).first().image_link
                upcoming_show['start_time'] = str(show.start_time)
                upcoming_shows.append(past_show)
            data['past_shows'] = past_shows
            data['upcoming_shows'] = upcoming_shows
            data['past_shows_count'] = len(past_shows)
            data['upcoming_shows_count'] = len(upcoming_shows)
    except:
        flash(
            f"Sorry, the venue of id {venue_id} no longer exists in our database.", category="info")
        abort(404)
    finally:
        return render_template('pages/show_venue.html', venue=data) if isFound else redirect('/404')

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    # print(form.name.data, form.city.data, form.state.data, \
    #       form.address.data, form.phone.data, form.image_link.data)
    # print(request.form['name'], request.form['city'], request.form['state'], request.form['address'],
    #       request.form['phone'], request.form['image_link'], request.form['genres'], request.form['seeking_talent'])
    try:
        venue = Venue(name=request.form['name'], city=request.form['city'], state=request.form['state'], address=request.form['address'], phone=request.form['phone'], image_link=request.form['image_link'],
                      genres=request.form.getlist('genres', type=str), facebook_link=request.form['facebook_link'], website=request.form['website_link'], seeking_talent="seeking_talent" in request.form, seeking_description=request.form['seeking_description'])
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash(f"Venue {request.form['name']} was successfully listed!")
    except:
        flash(f"Venue {request.form['name']} could not be listed!", category="error")
        db.session.rollback()
        abort(500)
    finally:
        db.session.close()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter(Venue.id == venue_id).delete()
        db.session.commit()
        db.session.close()
        flash(f'Venue with id {venue_id} was successfully deleted!')
    except:
        flash(f'Venue with id {venue_id} could not be deleted!', category="error")
        db.session.rollback()
        abort(500)
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    finally:
        return jsonify({"homeUrl": '/'})

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    try:
        result = Artist.query.all()
        data = []
        for artist in result:
            info = {}
            info['id'] = artist.id
            info['name'] = artist.name
            data.append(info)
    except:
        flash(
            f"Sorry due, to an issue on our end, we are unable to display the artists page.", category="error")
        abort(500)
    finally:
        return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 4,
    #         "name": "Guns N Petals",
    #         "num_upcoming_shows": 0,
    #     }]
    # }

    # print(request.form.get('search_term', ''))
    try:
        data = Artist.query.filter(db.func.lower(Artist.name).like(
            f"%{request.form['search_term'].lower()}%")).order_by('name').all()

        artists = []

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        for artist in data:
            info = {}
            info['id'] = artist.id
            info['name'] = artist.name
            info['num_upcoming_shows'] = Show.query.filter(
                db.and_(Show.start_time > current_time, Show.artist_id == artist.id)).count()
            artists.append(info)
        response = {
            "count": len(data),
            "data": artists
        }
    except:
        flash(f"Sorry, an error occurred while fetching your search results.", category="error")
        abort(500)
    finally:
        return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    # data1 = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "past_shows": [{
    #         "venue_id": 1,
    #         "venue_name": "The Musical Hop",
    #         "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    #     "genres": ["Jazz"],
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "300-400-5000",
    #     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "past_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    #     "genres": ["Jazz", "Classical"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "432-325-5432",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 3,
    # }
    # data = list(filter(lambda d: d['id'] ==
    #             artist_id, [data1, data2, data3]))[0]
    try:
        data = {}
        isFound = False
        artist_data = Artist.query.filter(Artist.id == artist_id).first()
        if artist_data:
            isFound = True
            data = {}
            data['id'] = artist_data.id
            data['name'] = artist_data.name
            data['genres'] = artist_data.genres
            data['city'] = artist_data.city
            data['state'] = artist_data.state
            data['phone'] = artist_data.phone
            data['website'] = artist_data.website
            data['facebook_link'] = artist_data.facebook_link
            data['seeking_venue'] = artist_data.seeking_venue
            data['seeking_description'] = artist_data.seeking_description
            data['image_link'] = artist_data.image_link
            past_shows = []
            upcoming_shows = []
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            past = Show.query.filter(
                db.and_(Show.start_time < current_time, Show.artist_id == artist_id)).all()
            for show in past:
                past_show = {}
                past_show['venue_id'] = show.venue_id
                past_show['venue_name'] = Venue.query.filter(
                    Venue.id == show.venue_id).first().name
                past_show['venue_image_link'] = Venue.query.filter(
                    Venue.id == show.venue_id).first().image_link
                past_show['start_time'] = str(show.start_time)
                past_shows.append(past_show)

            upcoming = Show.query.filter(
                db.and_(Show.start_time > current_time, Show.artist_id == artist_id)).all()
            for show in upcoming:
                upcoming_show = {}
                upcoming_show['venue_id'] = show.venue_id
                upcoming_show['venue_name'] = Venue.query.filter(
                    Venue.id == show.venue_id).first().name
                upcoming_show['venue_image_link'] = Venue.query.filter(
                    Venue.id == show.venue_id).first().image_link
                upcoming_show['start_time'] = str(show.start_time)
                upcoming_shows.append(upcoming_show)
            data['past_shows'] = past_shows
            data['upcoming_shows'] = upcoming_shows
            data['past_shows_count'] = len(past_shows)
            data['upcoming_shows_count'] = len(upcoming_shows)
    except:
        flash(
            f"Sorry, the artist of id {artist_id} no longer exists in our database.", category="info")
    finally:
        return render_template('pages/show_artist.html', artist=data) if isFound else redirect('/404')

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # artist = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    # TODO: populate form with fields from artist with ID <artist_id>
    try:
        data = Artist.query.filter(Artist.id == artist_id).first()
        artist_form = ArtistForm(name=data.name, city=data.city, state=data.state, phone=data.phone, image_link=data.image_link, genres=data.genres,
                                 facebook_link=data.facebook_link, website_link=data.website, seeking_venue=data.seeking_venue, seeking_description=data.seeking_description)
    except:
        flash(f"Sorry, unable to load up the Artist Edit form.", category="error")
        abort(500)
    finally:
        return render_template('forms/edit_artist.html', form=artist_form, artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        artist = Artist.query.filter(Artist.id == artist_id).first()
        artist.name = request.form['name']
        artist.genres = request.form.getlist('genres', type=str)
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.website = request.form['website_link']
        artist.facebook_link = request.form['facebook_link']
        artist.seeking_talent = 'seeking_venue' in request.form
        artist.seeking_description = request.form['seeking_description']
        artist.image_link = request.form['image_link']
        db.session.commit()
    except:
        flash(f"Sorry, the artist could not be updated.", category="error")
        db.session.rollback()
        abort(500)
    finally:
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # venue = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # TODO: populate form with values from venue with ID <venue_id>
    try:
        data = Venue.query.filter(Venue.id == venue_id).first()
        venue_form = VenueForm(name=data.name, city=data.city, state=data.state, phone=data.phone, address=data.address, image_link=data.image_link, genres=data.genres,
                               facebook_link=data.facebook_link, website_link=data.website, seeking_talent=data.seeking_talent, seeking_description=data.seeking_description)
    except:
        flash(f"Sorry, unable to load up the Venue Edit form.", category="error")
        abort(500)
    finally:
        return render_template('forms/edit_venue.html', form=venue_form, venue=data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        venue = Venue.query.filter(Venue.id == venue_id).first()
        venue.name = request.form['name']
        venue.genres = request.form.getlist('genres', type=str)
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.phone = request.form['phone']
        venue.website = request.form['website_link']
        venue.facebook_link = request.form['facebook_link']
        venue.seeking_talent = 'seeking_talent' in request.form
        venue.seeking_description = request.form['seeking_description']
        venue.image_link = request.form['image_link']
        db.session.commit()
    except:
        flash(f"Sorry, the venue could not be updated.")
        db.session.rollback()
        abort(500)
    finally:
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    artist_create_form = ArtistForm()
    return render_template('forms/new_artist.html', form=artist_create_form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    # print(request.form)
    try:
        if not Artist.query.filter(Artist.phone == request.form['phone']).count() > 0:
            artist = Artist(name=request.form['name'], city=request.form['city'], state=request.form['state'], phone=request.form['phone'], image_link=request.form['image_link'],
                            genres=request.form.getlist('genres', type=str), facebook_link=request.form['facebook_link'], website=request.form['website_link'], seeking_venue='seeking_venue' in request.form, seeking_description=request.form['seeking_description'])
            db.session.add(artist)
            db.session.commit()
            # on successful db insert, flash success
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
            flash(f"Artist {request.form['name']} was successfully listed!")
        else:
            flash('Phone number already exists', category="info")
            db.session.rollback()
            abort()
    except:
        flash(f"Sorry, the artist could not be listed.", category="error")
        db.session.rollback()
        abort(500)
    finally:
        return render_template('pages/home.html')


@app.route('/artists/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        Artist.query.filter(Artist.id == artist_id).delete()
        db.session.commit()
        db.session.close()
        flash(f"Artist with id { artist_id } was successfully deleted!")
    except:
        flash(f"Sorry, Artist with id { artist_id } could not be deleted!", category="error")
    finally:
        return jsonify({"homeUrl": '/'})

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    try:
        data = []

        shows = Show.query.all()

        for show in shows:
            info = {}
            info['venue_id'] = show.venue_id
            info['venue_name'] = Venue.query.filter(
                Venue.id == show.venue_id).first().name
            info['artist_id'] = show.artist_id
            info['artist_name'] = Artist.query.filter(
                Artist.id == show.artist_id).first().name
            info['artist_image_link'] = Artist.query.filter(
                Artist.id == show.artist_id).first().image_link
            info['start_time'] = str(show.start_time)
            data.append(info)
    except:
        flash(
            f"Sorry due, to an issue on our end, we are unable to display the shows page.", category="error")
        abort(500)
    finally:
        return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    try:
        show = Show(artist_id=request.form['artist_id'],
                    venue_id=request.form['venue_id'], start_time=request.form['start_time'])
        db.session.add(show)
        db.session.commit()
    # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('Show could not be listed!', category="error")
    finally:
        return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
