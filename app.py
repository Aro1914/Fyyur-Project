#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import datetime
# import json
import logging
import os
# from enum import unique
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import (Response, abort, flash, jsonify, redirect, render_template,
                   request, url_for)

from forms import *
from models import Artist, Show, Venue, app, db

# from flask_wtf import Form


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


# TODO: connect to a local postgresql database


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
    try:
        try:
            recently_listed_artists = db.session.query(Artist).order_by(
                Artist.id.desc()).limit(10).all()
        except:
            flash(f"Error fetching recently listed artists!")

        try:
            recently_listed_venues = db.session.query(Venue).order_by(
                Venue.id.desc()).limit(10).all()
        except:
            flash(f"Error fetching recently listed venues!")

        artists = []
        venues = []

        for artist in recently_listed_artists:
            info = {}
            info['id'] = artist.id
            info['name'] = artist.name
            artists.append(info)

        for venue in recently_listed_venues:
            info = {}
            info['id'] = venue.id
            info['name'] = venue.name
            venues.append(info)

        data = {
            "artists": artists,
            "venues": venues
        }
    except:
        flash(f"Sorry, could not fetch recently listed data!",
              category="error")
        abort(500)
    return render_template('pages/home.html', data=data)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
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


def get_venue_result(search_term):
    try:
        data = Venue.query.filter(db.func.lower(Venue.name).like(
            f"%{search_term.lower()}%")).order_by('name').all()
        return data
    except Exception as e:
        print(e)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    try:
        data = get_venue_result(request.form['search_term'])
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
        flash(f"Sorry, an error occurred while fetching your search results.",
              category="error")
        abort(500)
    finally:
        return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    try:
        data = {}
        venue_data = Venue.query.filter(Venue.id == venue_id).first()
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
        data['seeking_description'] = venue_data.seeking_description
        data['image_link'] = venue_data.image_link
        past_shows = []
        upcoming_shows = []
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        past = db.session.query(Show).join(Artist).filter(
            db.and_(Show.start_time < current_time, Show.venue_id == venue_id)).all()
        for show in past:
            past_show = {}
            past_show['artist_id'] = show.artist_id
            past_show['artist_name'] = show.artist.name
            past_show['artist_image_link'] = show.artist.image_link
            past_show['start_time'] = str(show.start_time)
            past_shows.append(past_show)

        upcoming = db.session.query(Show).join(Artist).filter(
            db.and_(Show.start_time > current_time, Show.venue_id == venue_id)).all()
        for show in upcoming:
            upcoming_show = {}
            upcoming_show['artist_id'] = show.artist_id
            upcoming_show['artist_name'] = show.artist.name
            upcoming_show['artist_image_link'] = show.artist.image_link
            upcoming_show['start_time'] = str(show.start_time)
            upcoming_shows.append(upcoming_show)
        data['past_shows'] = past_shows
        data['upcoming_shows'] = upcoming_shows
        data['past_shows_count'] = len(past_shows)
        data['upcoming_shows_count'] = len(upcoming_shows)
        return render_template('pages/show_venue.html', venue=data)
    except:
        flash(
            f"Sorry, the venue of id {venue_id} no longer exists in our database.", category="info")
        abort(404)
    return render_template('pages/show_venue.html', venue=data)

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
    form = VenueForm(request.form)
    if form.validate():
        try:
            venue = Venue(name=request.form['name'], city=request.form['city'], state=request.form['state'], address=request.form['address'], phone=request.form['phone'], image_link=request.form['image_link'],
                          genres=request.form.getlist('genres', type=str), facebook_link=request.form['facebook_link'], website=request.form['website_link'], seeking_talent="seeking_talent" in request.form, seeking_description=request.form['seeking_description'])
            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash(f"Venue '{request.form['name']}' was successfully listed!")
            return redirect(url_for('show_venue', venue_id=Venue.query.order_by(Venue.id.desc()).first().id))
        except:
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            flash(
                f"Venue '{request.form['name']}' could not be listed!", category="error")
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()
    else:
        for message in form.errors.items():
            flash(f"{str(message)[2:len(str(message))-2]}!", category="danger")
    return redirect(url_for('index'))


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter(Venue.id == venue_id).delete()
        db.session.commit()
        flash(f'Venue with id {venue_id} was successfully deleted!')
    except:
        flash(
            f'Venue with id {venue_id} could not be deleted!', category="error")
        db.session.rollback()
        abort(500)
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    finally:
        db.session.close()
        return jsonify({"homeUrl": '/'})

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
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


def get_artist_result(search_term):
    try:
        data = Artist.query.filter(db.func.lower(Artist.name).like(
            f"%{search_term.lower()}%")).order_by('name').all()
        return data
    except Exception as e:
        print(e)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    try:
        data = get_artist_result(request.form['search_term'])

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
        flash(f"Sorry, an error occurred while fetching your search results.",
              category="error")
        abort(500)
    finally:
        return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    try:
        artist_data = Artist.query.filter(Artist.id == artist_id).first()
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

        past = db.session.query(Show).join(Venue).filter(
            db.and_(Show.start_time < current_time, Show.artist_id == artist_id)).all()
        for show in past:
            past_show = {}
            past_show['venue_id'] = show.venue_id
            past_show['venue_name'] = show.venue.name
            past_show['venue_image_link'] = show.venue.image_link
            past_show['start_time'] = str(show.start_time)
            past_shows.append(past_show)

        upcoming = db.session.query(Show).join(Venue).filter(
            db.and_(Show.start_time > current_time, Show.artist_id == artist_id)).all()
        for show in upcoming:
            upcoming_show = {}
            upcoming_show['venue_id'] = show.venue_id
            upcoming_show['venue_name'] = show.venue.name
            upcoming_show['venue_image_link'] = show.venue.image_link
            upcoming_show['start_time'] = str(show.start_time)
            upcoming_shows.append(upcoming_show)
        data['past_shows'] = past_shows
        data['upcoming_shows'] = upcoming_shows
        data['past_shows_count'] = len(past_shows)
        data['upcoming_shows_count'] = len(upcoming_shows)
    except:
        flash(
            f"Sorry, the artist of id {artist_id} no longer exists in our database.", category="info")
        abort(404)
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
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
    form = ArtistForm(request.form)
    if form.validate():
        try:
            artist = Artist.query.filter(Artist.id == artist_id).first()
            artist.name = request.form['name']
            artist.genres = request.form.getlist('genres', type=str)
            artist.city = request.form['city']
            artist.state = request.form['state']
            artist.phone = request.form['phone']
            artist.website = request.form['website_link']
            artist.facebook_link = request.form['facebook_link']
            artist.seeking_venue = 'seeking_venue' in request.form
            artist.seeking_description = request.form['seeking_description']
            artist.image_link = request.form['image_link']
            db.session.commit()
            flash(f"Artist updated!")
        except:
            flash(f"Sorry, the artist could not be updated.", category="error")
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()
    else:
        for message in form.errors.items():
            flash(f"{str(message)[2:len(str(message))-2]}!", category="danger")
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
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
    form = VenueForm(request.form)
    if form.validate():
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
            flash(f"Venue updated!")
        except:
            flash(f"Sorry, the venue could not be updated.")
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()
    else:
        for message in form.errors.items():
            flash(f"{str(message)[2:len(str(message))-2]}!", category="danger")
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
    form = ArtistForm(request.form)
    if form.validate():
        try:
            phoneExists = False
            if not Artist.query.filter(Artist.phone == request.form['phone']).count() > 0:
                artist = Artist(name=request.form['name'], city=request.form['city'], state=request.form['state'], phone=request.form['phone'], image_link=request.form['image_link'],
                                genres=request.form.getlist('genres', type=str), facebook_link=request.form['facebook_link'], website=request.form['website_link'], seeking_venue='seeking_venue' in request.form, seeking_description=request.form['seeking_description'])
                db.session.add(artist)
                db.session.commit()
                # on successful db insert, flash success
                # TODO: on unsuccessful db insert, flash an error instead.
                # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
                flash(
                    f"Artist '{request.form['name']}' was successfully listed!")
                return redirect(url_for('show_artist', artist_id=Artist.query.order_by(Artist.id.desc()).first().id))
            else:
                phoneExists = True
                raise
        except:
            flash(
                f"Sorry, the artist could not be listed{' because the phone number provided already exists in our database' if phoneExists else ''}!", category="error")
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()
    else:
        for message in form.errors.items():
            flash(f"{str(message)[2:len(str(message))-2]}!", category="danger")
    return redirect(url_for('index'))


@app.route('/artists/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        Artist.query.filter(Artist.id == artist_id).delete()
        db.session.commit()
        flash(f"Artist with id { artist_id } was successfully deleted!")
    except:
        flash(
            f"Sorry, Artist with id { artist_id } could not be deleted!", category="error")
        db.session.rollback()
        abort(500)
    finally:
        db.session.close()
        return jsonify({"homeUrl": '/'})

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
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


@app.route('/shows/search', methods=['POST'])
def search_show():
    response = {}
    try:
        shows = []
        print(request.form['filter_by'], request.form['filter_by'])
        if request.form['filter_by'] == 'venue':
            shows = db.session.query(Show).join(Venue).filter(Show.venue_id == Venue.id).filter(db.func.lower(Venue.name).like(
                f"%{request.form['search_term'].lower()}%")).order_by('id').all()
        if request.form['filter_by'] == 'artist':
            shows = db.session.query(Show).join(Artist).filter(Show.artist_id == Artist.id).filter(db.func.lower(Artist.name).like(
                f"%{request.form['search_term'].lower()}%")).order_by('id').all()
        print(shows)
        data = []

        for show in shows:
            info = {}
            info['venue_id'] = show.venue_id
            info['venue_name'] = show.venue.name
            info['artist_id'] = show.artist_id
            info['artist_name'] = show.artist.name
            info['artist_image_link'] = show.artist.image_link
            info['start_time'] = str(show.start_time)
            data.append(info)
            response["count"] = len(shows)
            response["data"] = data
    except:
        flash(
            f"Sorry, an error occurred while fetching your search results.", category="error")
        db.session.close()
        abort(500)
    finally:
        return render_template('pages/search_show.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    def get_artist_list ():
        choices = []
        artists = db.session.query(Artist).all()
        for artist in artists:
            choices.append((artist.id, artist.id))
    
        return choices

    def get_venue_list ():
        choices = []
        venues = db.session.query(Venue).all()        
        for venue in venues:
            choices.append((venue.id, venue.id))
        
        return choices
    form = ShowForm()

    form.artist_id.choices = get_artist_list()
    form.venue_id.choices = get_venue_list()

    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    try:
        artistFound = True
        venueFound = True
        if Artist.query.filter(Artist.id == request.form['artist_id']).count() == 0:
            artistFound = False
            raise ValueError

        if Venue.query.filter(Venue.id == request.form['venue_id']).count() == 0:
            venueFound = False
            raise ValueError

        show = Show(artist_id=request.form['artist_id'],
                    venue_id=request.form['venue_id'], start_time=datetime.fromisoformat(str(request.form['start_time'])))
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except ValueError as e:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash(
            f"""Show could not be listed{f" because the {'Artist' if not artistFound else 'Venue' if not venueFound else ''} ID provided does not exist in our database" if not artistFound or not venueFound else f', because {e}'}!""", category="error")
        db.session.rollback()
        abort(500)
    except Exception as e:
        flash(
            f"""Show could not be listed{f', because {e}'}!""", category="error")
        db.session.rollback()
        abort(500)
    finally:
        db.session.close()
    return redirect(url_for('index'))


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
