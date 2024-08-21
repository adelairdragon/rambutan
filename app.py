from datetime import datetime
import tomllib
import random

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import sqlalchemy

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

# print("Config:", config)

server_name = config.get('rambutan', {}).get('title')

if server_name is None:
    server_name = "Rambutan Example Deployment"

# Configure the SQLAlchemy connection string based on the DB_TYPE environment variable
db_type = config['db'].get('type', 'sqlite')  # Default to SQLite if not set

if db_type == 'mysql':
    drivername = 'mysql+mysqlconnector'
elif db_type == 'postgresql':
    drivername = 'postgresql+psycopg2'
elif db_type == 'sqlite':
    drivername = 'sqlite'
else:
    raise ValueError("Unsupported DB_TYPE. Choose from 'mysql', 'postgresql', or 'sqlite'.")

if db_type == "sqlite":
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{config['db']['host']}"
else:
    url_object = sqlalchemy.URL.create(
        drivername,
        username = config['db']['user'],
        password = config['db']['password'],
        host =     config['db']['host'],
        port =     config['db']['port'],
        database = config['db']['database']
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = url_object

# app.config['SQLALCHEMY_ECHO'] = True
# print("DB URI:", app.config['SQLALCHEMY_DATABASE_URI'])

lychee_base_url = config['lychee']['base_url']

# Initialize SQLAlchemy
db.init_app(app)

with app.app_context():
    db.reflect()
    # inspection = sqlalchemy.inspect(db.engine)
    # print("Tables:", inspection.get_table_names())


# Photo Model
class Photos(db.Model):
    __table__ = db.metadata.tables["photos"]

class SizeVariants(db.Model):
    __table__ = db.metadata.tables["size_variants"]

class Albums(db.Model):
    __table__ = db.metadata.tables["base_albums"]

@app.route('/')
def index():
    starred_photo_results = db.session.execute(db.select(Photos).filter_by(is_starred=True)).scalars()
    starred_photos = starred_photo_results.all()
    random_photo_results = random.choices(starred_photos, k=3)
    random_photos = []
    for photo in random_photo_results:
        photo_gallery_link = f'{lychee_base_url}/gallery/{photo.album_id}/{photo.id}'
        album_link = f'{lychee_base_url}/gallery/{photo.album_id}'

        album = db.session.execute(db.select(Albums).filter_by(id=photo.album_id)).scalar_one()

        size_variant = db.session.execute(db.select(SizeVariants).filter_by(photo_id=photo.id, type=1)).scalar()
        if size_variant is None:
            size_variant = db.session.execute(db.select(SizeVariants).filter_by(photo_id=photo.id, type=0)).scalar_one()
        photo_raw_link = f'{lychee_base_url}/uploads/{size_variant.short_path}'

        random_photos.append({"gallery_link": photo_gallery_link, 
                              "raw_link": photo_raw_link,
                              "album_title": album.title,
                              "album_link": album_link,
                              "address": photo.location,
                              "camera_body": photo.model,
                              "lens": photo.lens,
                              "aperture": photo.aperture,
                              "shutter_speed": photo.shutter,
                              "focal_length": photo.focal})
    
    return render_template('index.html', current_time=datetime.now().strftime("%A, %d. %B %Y %I:%M%p"), photo_links=random_photos, server_name=server_name)

if __name__ == '__main__':
    app.run(debug=True)