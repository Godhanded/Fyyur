#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from hmac import new
import json
from optparse import Values
from os import abort
import sys
from time import time
from unicodedata import name
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template,
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
  )
from flask_moment import Moment

import logging
from logging import (
    Formatter, 
    FileHandler
  )
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# from models import *

from models import *

db.init_app(app)
migrate=Migrate(app,db)
  
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
# from controllers import *
@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  values= Venue.query.all()
  now= datetime.now()
  num_upcuming=0
  for v in values:
    shows= Shows.query.filter_by(venue_id=v.id).all()
    for show in shows:
      if show.start_time> now:
        num_upcuming+=1
        
    venues=[{
      "id":v.id,
      "name":v.name,
      "num_upcoming_shows":num_upcuming
    }]
    num_upcuming=0
    data.append({
      "city":v.city,
      "state":v.state,
      "venues":venues
    })
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  
  # data[venues]=id=data.id, name= data.name,num_upcoming_shows=shows.query.all().count()
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  data= Venue.query.filter(Venue.name.ilike('%'+request.form['search_term']+'%'))
  now= datetime.now()
  values=[]
  show_no=0
  for d in data:
    upcoming=Shows.query.filter_by(venue_id=d.id).all()
    for show in upcoming:
      if show.start_time> now:
        show_no+=1
    values.append({
      "id":d.id,
      "name":d.name,
      "num_upcoming_shows":show_no
    })
    show_no=0
  response={"count":data.count(),
            "data":values,
            }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  datas= Venue.query.get(venue_id)
  upcoming_shows_data=db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).filter(Shows.start_time>datetime.now()).all()
  past_shows_data=db.session.query(Shows).join(Artist).filter(Shows.venue_id==venue_id).filter(Shows.start_time<datetime.now()).all()
  past_shows_count=0
  upcoming_shows_count=0
  upcoming_shows=[]
  past_shows=[]
  for shows in upcoming_shows_data:
    upcoming_shows.append({
      "artist_id":shows.artist_id,
      "artist_name":shows.artists.name,
      "artist_image_link": shows.artists.image_link,
      "start_time":format_datetime(str(shows.start_time))
    })
    upcoming_shows_count+=1
  for shows in past_shows_data:
    past_shows.append({
      "artist_id":shows.artist_id,
      "artist_name":shows.artists.name,
      "artist_image_link": shows.artists.image_link,
      "start_time":format_datetime(str(shows.start_time))
    })
    past_shows_count+=1

  genres=[genre.name for genre in datas.genres]
  data={
    "id": datas.id,
    "name":datas.name,
    "genres":genres,
    "address":datas.address,
    "city":datas.city,
    "state":datas.state,
    "phone":datas.phone,
    "website":datas.website_link,
    "facebook_link":datas.facebook_link,
    "seeking_talent":datas.seeking_talent,
    "seeking_description":datas.seeking_description,
    "image_link":datas.image_link,
    "past_shows": past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count":upcoming_shows_count
  }
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form=VenueForm()
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error= False
  name=request.form['name']
  if Venue.query.filter_by(name=name).first() is None:
    try:
      Name= request.form['name'] 
      print (Name)
      City= request.form['city'] 
      State= request.form['state'] 
      Address=  request.form['address'] 
      Phone=  request.form['phone'] 
      image=  request.form['image_link'] 
      genres= request.form['genres']
      facebook= request.form['facebook_link'] 
      website= request.form['website_link'] 
      talent=  form.seeking_talent.data #True if request.form['seeking_talent'] is not None else False
      print(talent)
      # talent= bool(talent)
      desc= request.form['seeking_description'] 
      record= Venue(name= Name,city=City,state=State,address=Address,phone=Phone,image_link=image,facebook_link=facebook,website_link=website,seeking_talent=talent,seeking_description=desc)
      for genre in genres:
        new_genre= Genre.query.filter_by(name=genre).one_or_none()
        if new_genre:
          record.genres.append(new_genre)
        else:
          new_genre= Genre(name=genre)
          db.session.add(new_genre)
          record.genres.append(new_genre)
      db.session.add(record)
      db.session.commit()
    except:
      db.session.rollback()
      error=True
      print (sys.exc_info())
    finally:
      db.session.close()
    # on successful db insert, flash success
    if(error):
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      
    else:
      # dbname=Venue.query.filter_by(name=request.form['name'])
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    flash('Venue already exist')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error= False
  try:
    data= Venue.query.get(venue_id)
    db.session.delete(data)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print (sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash("failed to delete venue with id: "+venue_id)
  else:
    flash('sucsessfully removed venue with id: '+ venue_id)
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  data=[]
  values=Artist.query.all()
  for v in values:
    data.append({"id":v.id,
                 "name":v.name})
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  num_upcoming=0
  data=[]
  now= datetime.now()
  values= Artist.query.filter(Artist.name.ilike("%"+request.form['search_term']+"%"))
  for v in values:
    show=Shows.query.filter_by(venue_id=v.id).all()
    for shows in show:
      if shows.start_time>now:
        num_upcoming+=1
    data.append({
      "id":v.id,
      "name":v.name,
      "num_upcoming_shows":num_upcoming
    })
    num_upcoming=0
  response={"count":values.count(),"data":data}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  datas= Artist.query.get(artist_id)
  upcoming_show_data= db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist_id).filter(Shows.start_time>datetime.now()).all()
  past_shows_count=0
  upcoming_shows_count=0
  upcoming_shows=[]
  past_shows=[]
  past_show_data=db.session.query(Shows).join(Venue).filter(Shows.artist_id==artist_id).filter(Shows.start_time<datetime.now()).all()
  for shows in upcoming_show_data:
    upcoming_shows.append({
    "venue_id":shows.venue_id,
    "venue_name":shows.venues.name,
    "venue_image_link": shows.venues.image_link,
    "start_time":format_datetime(str(shows.start_time))
    })
    upcoming_shows_count+=1
  for shows in past_show_data:

    past_shows.append({
      "venue_id":shows.venue_id,
      "venue_name":shows.venues.name,
      "venue_image_link": shows.venues.image_link,
      "start_time":format_datetime(str(shows.start_time))
    })
    past_shows_count+=1
  genres=[genre.name for genre in datas.genres]

  data={
    "id": datas.id,
    "name":datas.name,
    "genres":genres,
    "city":datas.city,
    "state":datas.state,
    "phone":datas.phone,
    "website":datas.website_link,
    "facebook_link":datas.facebook_link,
    "seeking_venue":datas.seeking_venue,
    "seeking_description":datas.seeking_description,
    "image_link":datas.image_link,
    "past_shows": past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count":upcoming_shows_count
  }

  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  
  # TODO: populate form with fields from artist with ID <artist_id>
  artist=Artist.query.get(artist_id)
  genres=[genre.name for genre in artist.genres]
  form = ArtistForm(name=artist.name,
          city=artist.city,
          state=artist.state,
          phone=artist.phone,
          image_link=artist.image_link,
          genres=genres,
          facebook_link=artist.facebook_link,
          website_link=artist.website_link,
          seeking_venue= artist.seeking_venue,
          seeking_description=artist.seeking_description)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist=Artist.query.get(artist_id)
  error=False
  try:
    artist.name= request.form['name'] 
    artist.city= request.form['city'] 
    artist.state= request.form['state'] 
    artist.phone=  request.form['phone'] 
    artist.image_link=  request.form['image_link'] 
    genres= request.form['genres']
    artist.facebook_link= request.form['facebook_link'] 
    artist.website_link= request.form['website_link'] 
    artist.seeking_venue=  form.seeking_venue.data #True if request.form['seeking_venue'] is not None else False
    artist.seeking_description= request.form['seeking_description']
    artist.genres=[]
    for genre in genres:
      get_genre=Genre.query.filter_by(name=genre).one_or_none()
      if get_genre:
        artist.genres.append(get_genre)
      else:
        new_genre=Genre(name=genre)
        db.session.add(new_genre)
        artist.genres.append(new_genre)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
  finally:
    db.session.close()
  if error:
    flash('failed to update Artist with id: '+ artist_id)
  else:
    flash('Artist with id: '+str(artist_id)+' updated sucessfully')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue=Venue.query.get(venue_id)
  genres=[genre.name for genre in venue.genres]
  form = VenueForm(name=venue.name,
          city=venue.city,
          state=venue.state,
          address=venue.address,
          phone=venue.phone,
          image_link=venue.image_link,
          genres=genres,
          facebook_link=venue.facebook_link,
          website_link=venue.website_link,
          seeking_talent= venue.seeking_talent,
          seeking_description=venue.seeking_description)
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue=Venue.query.get(venue_id)
  form = VenueForm()
  error=False
  try:
    venue.name= request.form['name'] 
    venue.city= request.form['city'] 
    venue.state= request.form['state'] 
    venue.address=  request.form['address'] 
    venue.phone=  request.form['phone']
    genres=request.form['genres'] 
    venue.genres=[]
    venue.image_link=  request.form['image_link'] 
    venue.facebook_link= request.form['facebook_link'] 
    venue.website_link= request.form['website_link'] 
    venue.seeking_talent= form.seeking_talent.data #True if request.form['seeking_talent'] is not None else False
    venue.seeking_description= request.form['seeking_description']
    for genre in genres:
      get_genre=Genre.query.filter_by(name=genre).one_or_none()
      if get_genre:
        venue.genres.append(get_genre)
      else:
        new_genre=Genre(name=genre)
        db.session.add(new_genre)
        venue.genres.append(new_genre)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
  finally:
    db.session.close()
  if error:
    abort(500)
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error= False
  artist=Artist.query.filter_by(name=request.form['name']).first()
  form = ArtistForm()
  if artist is None:
    try:
      Name= request.form['name'] 
      City= request.form['city'] 
      State= request.form['state'] 
      genres=  request.form['genres'] 
      Phone=  request.form['phone'] 
      image=  request.form['image_link'] 
      facebook= request.form['facebook_link'] 
      website= request.form['website_link'] 
      venue=  form.seeking_venue.data# True if request.form['seeking_venue'] is not None else False
      print (venue)
      desc= request.form['seeking_description'] 
      record= Artist(name= Name,city=City,state=State,phone=Phone,image_link=image,facebook_link=facebook,website_link=website,seeking_venue=venue,seeking_description=desc)
      for genre in genres:
        get_genre=Genre.query.filter_by(name=genre).one_or_none()
        if get_genre:
          record.genres.append(get_genre)
        else:
          new_genre=Genre(name=genre)
          db.session.add(new_genre)
          record.genres.append(new_genre)
      db.session.add(record)
      db.session.commit()
    except:
      db.session.rollback()
      error=True
      print (sys.exc_info())
    finally:
      db.session.close()
    if error:
      flash('An error occurred. Artist ' + Name + ' could not be listed.')      
    else:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('sorry Artist already exists')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  show_list= Shows.query.all()
  data=[]
  for show in show_list:
    data.append({
      "venue_id":show.venue_id,
      "venue_name":show.venues.name,
      "artist_id":show.artist_id,
      "artist_name": show.artists.name,
      "artist_image_link":show.artists.image_link,
      "start_time": format_datetime(str(show.start_time))
    })
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
    error= False
    artist_id= request.form['artist_id']
    venue_id= request.form['venue_id']
    starttime= request.form['start_time']
    record=Shows(artist_id=artist_id, venue_id=venue_id,start_time=starttime)
    db.session.add(record)
    db.session.commit()
  except:
    db.session.rollback()
    print (sys.exc_info())
    error=True
    # print (sys.exc_info())
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')

  # on successful db insert, flash success
  

  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
