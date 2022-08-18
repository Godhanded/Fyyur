from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class Genre(db.Model):
  __tablename__ = 'genre'
  id= db.Column(db.Integer, primary_key=True)
  name= db.Column(db.String(),nullable=False)

artist_genres=db.Table('artist_genre',
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'),primary_key=True),
    db.Column('artist_id',db.Integer,db.ForeignKey('artist.id'),primary_key=True)
)

venue_genres=db.Table('venue_genre',
    db.Column('genre_id',db.Integer,db.ForeignKey('genre.id'), primary_key=True),
    db.Column('venue_id',db.Integer,db.ForeignKey('venue.id'), primary_key=True)
  )


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres= db.relationship('Genre',secondary=venue_genres,backref=db.backref('venues',lazy=True))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(),nullable=False,default=False)
    seeking_description = db.Column(db.String())
    shows= db.relationship('Shows', backref="venues",lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Shows(db.Model):
  __tablename__ = 'shows'
  id=db.Column(db.Integer,primary_key=True)
  artist_id=db.Column(db.Integer, db.ForeignKey('artist.id'),nullable=False)
  venue_id=db.Column(db.Integer, db.ForeignKey('venue.id'),nullable=False)
  start_time=db.Column(db.DateTime, nullable=False)
  

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('Genre',secondary=artist_genres,backref=db.backref('artists',lazy=True))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,nullable=False,default= False)
    seeking_description = db.Column(db.String())
    shows= db.relationship('Shows', backref="artists",lazy=True)