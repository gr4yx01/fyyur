#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import ARRAY, TIMESTAMP, DateTime, Table, and_, or_, desc
from forms import *
from flask_migrate import Migrate
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
db.init_app(app)

migrate = Migrate(app, db)

app.config.from_object('config')

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


@ app.route('/')
def index():
    venues = Venue.query.order_by(desc(Venue.id)).limit(10).all()
    artists = Artist.query.order_by(desc(Artist.id)).limit(10).all()

    venue_data = []
    artist_data = []

    for venue in venues:
        venue_data.append(venue.name)

    for artist in artists:
        artist_data.append(artist.name)

    print(venues)
    return render_template('pages/home.html', artists=artist_data, venues=venue_data)


#  Venues
#  ----------------------------------------------------------------

@ app.route('/venues')
def venues():
    # TODO: replace with real venues data. => DONE
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venues = Venue.query.all()
    data = []

    for venue in venues:
        item = {}
        item['city'] = venue.city
        item['state'] = venue.state
        item['venues'] = []
        duplicate = False

        # Check for duplicate
        for venue in data:
            if venue['city'] == item['city'] and venue['state'] == item['state']:
                duplicate = True
                break

        if duplicate:
            duplicate = False
            break

        venueList = Venue.query.filter(and_(
            Venue.city == item['city'], Venue.state == item['state'])).all()

        for venue in venueList:
            num_of_upcoming_shows = db.session.query(Show).join(
                Venue).filter(Venue.id == venue.id).count()

            item['venues'].append(
                {'id': venue.id, 'name': venue.name, 'num_of_upcoming_shows': num_of_upcoming_shows})

        data.append(item)

    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive. => TODO
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term')
    data = []
    item = {}
    current_time = int(round(datetime.now().timestamp()))

    query_venue = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')).all()

    for venue in query_venue:
        upcoming_show = []
        item['id'] = venue.id
        item['name'] = venue.name
        # Get upcoming shows
        for show in venue.artists:
            time = int(round(show.start_time.timestamp()))
            if time > current_time:
                upcoming_show.append(show)

        item['num_upcoming_show'] = len(upcoming_show)
        data.append(item)

    response = {
        "count": len(query_venue),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id  => DONE
    past_s = []
    upcoming_s = []
    past_s_details = []
    upcoming_s_details = []
    current_venue = Venue.query.get(venue_id)
    shows = current_venue.artists  # Return show per venue
    data = {}

    current_time = datetime.now()
    current_time = int(round(current_time.timestamp()))

    for show in shows:
        time = int(round(show.start_time.timestamp()))
        if time > current_time:
            upcoming_s.append(show)
        else:
            past_s.append(show)

    if len(upcoming_s) >= 1:
        for show in upcoming_s:
            item = {}
            artist = show.artist
            item['artist_id'] = artist.id
            item['artist_name'] = artist.name
            item['artist_image_link'] = artist.image_link
            item['start_time'] = str(show.start_time)
            upcoming_s_details.append(item)

    if len(past_s) >= 1:
        for show in past_s:
            item = {}
            artist = show.artist
            item['artist_id'] = artist.id
            item['artist_name'] = artist.name
            item['artist_image_link'] = artist.image_link
            item['start_time'] = str(show.start_time)
            past_s_details.append(item)

    data = {
        "id": current_venue.id,
        "name": current_venue.name,
        "genres": current_venue.genres,
        "address": current_venue.address,
        "city": current_venue.city,
        "state": current_venue.state,
        "phone": current_venue.phone,
        "website": current_venue.website,
        "facebook_link": current_venue.facebook_link,
        "seeking_talent": current_venue.seeking_talent,
        "image_link": current_venue.image_link,
        "seeking_description": current_venue.seeking_description,
        "past_shows": past_s_details,
        "upcoming_shows": upcoming_s_details,
        "past_shows_count": len(past_s),
        "upcoming_shows_count": len(upcoming_s),
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()

    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()

    # TODO: insert form data as a new Venue record in the db, instead   => DONE
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    genres = form.genres.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website = form.website_link.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data

    # TODO: modify data to be the data object returned from db insertion     => DONE
    error = False

    try:
        venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link,
                      website=website,
                      image_link=image_link,
                      seeking_talent=seeking_talent, seeking_description=seeking_description)
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()

    if not error:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead. => DONE
        # flash('An error occurred.' + name + ' could not be listed')
    else:
        flash('An error occurred ' + name + ' could not be listed')

    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    return render_template('pages/home.html')


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using => TODO
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    current_venue = Venue.query.get(venue_id)

    try:
        db.session.delete(current_venue)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database => DONE
    artists = Artist.query.all()
    data = []

    for artist in artists:
        data.append({'id': artist.id, 'name': artist.name})

    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. => TODO
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term')
    data = []
    item = {}
    current_time = int(round(datetime.now().timestamp()))

    query_artist = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).all()

    for artist in query_artist:
        upcoming_show = []
        item['id'] = artist.id
        item['name'] = artist.name
        # Get upcoming shows
        for show in artist.venues:
            time = int(round(show.start_time.timestamp()))
            if time > current_time:
                upcoming_show.append(show)

        item['num_upcoming_show'] = len(upcoming_show)
        data.append(item)

    response = {
        "count": len(query_artist),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id => DONE
    past_s = []
    upcoming_s = []
    past_s_details = []
    upcoming_s_details = []
    artist = Artist.query.get(artist_id)

    shows = artist.venues  # Return show per artist
    data = {}

    current_time = datetime.now()
    current_time = int(round(current_time.timestamp()))

    for show in shows:
        time = int(round(show.start_time.timestamp()))
        if time > current_time:
            upcoming_s.append(show)
        else:
            past_s.append(show)

    if len(upcoming_s) >= 1:
        for show in upcoming_s:
            item = {}
            venue = show.venue
            item['venue_id'] = venue.id
            item['venue_name'] = venue.name
            item['venue_image_link'] = venue.image_link
            item['start_time'] = str(show.start_time)
            upcoming_s_details.append(item)

    if len(past_s) >= 1:
        for show in past_s:
            item = {}
            venue = show.venue
            item['venue_id'] = venue.id
            item['venue_name'] = venue.name
            item['venue_image_link'] = venue.image_link
            item['start_time'] = str(show.start_time)
            past_s_details.append(item)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_s_details,
        "upcoming_shows": upcoming_s_details,
        "past_shows_count": len(past_s),
        "upcoming_shows_count": len(upcoming_s),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    current_artist = Artist.query.get(artist_id)

    artist = {
        "id": current_artist.id,
        "name": current_artist.name,
        "genres": current_artist.genres,
        "city": current_artist.city,
        "state": current_artist.state,
        "phone": current_artist.phone,
        "website": current_artist.website,
        "facebook_link": current_artist.facebook_link,
        "seeking_venue": current_artist.seeking_venue,
        "seeking_description": current_artist.seeking_description,
        "image_link": current_artist.image_link
    }

    # TODO: populate form with fields from artist with ID <artist_id> => DONE

    form.name.data = current_artist.name
    form.city.data = current_artist.city
    form.state.data = current_artist.state
    form.phone.data = current_artist.phone
    form.genres.data = current_artist.genres
    form.facebook_link.data = current_artist.facebook_link
    form.image_link.data = current_artist.image_link
    form.website_link.data = current_artist.website
    form.seeking_venue.data = current_artist.seeking_venue
    form.seeking_description.data = current_artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing => DONE
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)

    form = ArtistForm()
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    try:
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    current_venue = Venue.query.get(venue_id)

    venue = {
        "id": current_venue.id,
        "name": current_venue.name,
        "genres": current_venue.genres,
        "address": current_venue.address,
        "city": current_venue.city,
        "state": current_venue.state,
        "phone": current_venue.phone,
        "website": current_venue.website,
        "facebook_link": current_venue.facebook_link,
        "seeking_talent": current_venue.seeking_talent,
        "seeking_description": current_venue.seeking_description,
        "image_link": current_venue.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id> => DONE

    form.name.data = current_venue.name
    form.city.data = current_venue.city
    form.state.data = current_venue.state
    form.phone.data = current_venue.phone
    form.genres.data = current_venue.genres
    form.address.data = current_venue.address
    form.facebook_link.data = current_venue.facebook_link
    form.image_link.data = current_venue.image_link
    form.website_link.data = current_venue.website
    form.seeking_talent.data = current_venue.seeking_talent
    form.seeking_description.data = current_venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing => DONE
    # venue record with ID <venue_id> using the new attributes

    venue = Venue.query.get(venue_id)

    form = VenueForm()
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.address = form.address.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    try:
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue.id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead => DONE
    form = ArtistForm()
    # TODO: modify data to be the data object returned from db insertion    => DONE

    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    facebook_link = form.facebook_link.data
    image_link = form.image_link.data
    website = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data

    error = False
    try:
        artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link,
                        website=website,
                        image_link=image_link,
                        seeking_venue=seeking_venue, seeking_description=seeking_description)
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()

    if not error:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead. => DONE
    else:
        flash('An error occurred. Artist ' +
              name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data. => DONE
    venues = Venue.query.all()
    artists = Artist.query.all()
    data = []

    for venue in venues:
        item = {}
        item['venue_id'] = venue.id
        item['venue_name'] = venue.name
        # Return show object which I would use to get artist object
        shows = venue.artists
        for show in shows:
            if len(shows) > 1:
                item = {}
                item['venue_id'] = venue.id
                item['venue_name'] = venue.name

            item['start_time'] = str(show.start_time)
            item['artist_id'] = show.artist.id
            item['artist_name'] = show.artist.name
            item['artist_image_link'] = show.artist.image_link

            if len(shows) > 1:
                data.append(item)
            else:
                data.append(item)

    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead => DONE
    form = ShowForm()
    artist_id = form.artist_id.data
    artist = Artist.query.filter(Artist.id == artist_id).first()

    venue_id = form.venue_id.data
    venue = Venue.query.filter(Venue.id == venue_id).first()
    start_time = form.start_time.data
    error = False

    try:
        show = Show(artist_id=artist_id, venue_id=venue_id,
                    start_time=start_time)
        show.venue = venue
        show.artist = artist

        db.session.add(venue)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if not error:
        #     # on successful db insert, flash success

        flash('Show was successfully listed!')
    # # TODO: on unsuccessful db insert, flash an error instead. => DONE
    else:
        flash("Bear with us as show could not be listed")
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
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
if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
