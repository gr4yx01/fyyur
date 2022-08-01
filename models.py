from collections import UserList
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY, TIMESTAMP


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

db = SQLAlchemy()


class Show(db.Model):
    __tablename__ = "shows"

    artist_id = db.Column(db.ForeignKey('artists.id'), primary_key=True)
    venue_id = db.Column(db.ForeignKey('venues.id'), primary_key=True)
    start_time = db.Column(TIMESTAMP(timezone=True), )
    artist = db.relationship(
        'Artist', lazy=False, back_populates='venues', uselist=False,)
    venue = db.relationship('Venue', lazy=False,
                            back_populates='artists', uselist=False,)

    def __repr__(self):
        return f'<Show artist={self.artist_id}, venue={self.venue_id}, start_time ={self.start_time}>'


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String()))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    artists = db.relationship(
        'Show', back_populates='venue', lazy=False, cascade='delete')

    def __repr__(self):
        return f'<Venue id={self.id} name={self.name}, genres={self.genres}, seeking_talent={self.seeking_talent}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    venues = db.relationship(
        Show, back_populates='artist', lazy=False,)

    def __repr__(self):
        return f'<Artist name={self.name}, genres={self.genres}, seeking_venue={self.seeking_venue}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
