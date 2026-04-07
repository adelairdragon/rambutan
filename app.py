from datetime import datetime
import tomllib
import random
import secrets
import os

from flask import Flask, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import sqlalchemy

def get_lychee_version(lychee_version):
    """
    Calculate Lychee's major/minor/patch version.
    Pass the "version" config value from the "configs" table.
    Tested on v5 and v7 databases.

    Examples:
    >>> get_lychee_version(70503)
    {'major': 7, 'minor': 5, 'patch': 3}
    >>> get_lychee_version(50501)
    {'major': 5, 'minor': 5, 'patch': 1}
    """
    # For now, this is an int. I bet it won't remain like this, but we'll cross that bridge when we get to it.
    lychee_version_int = int(lychee_version)
    major = lychee_version_int // 10000
    minor = (lychee_version_int % 10000) // 100
    patch = lychee_version_int % 100
    return {"major": major, "minor": minor, "patch": patch}

def get_highlighted_filter(major, minor=0, patch=0):
    """
    Get a dict for an SQLAlchemy `filter_by` statement to filter for highlighted/starred photos.
    Before version 7, photos were "starred" instead of "highlighted".
    """
    if major >= 7:
        return {"is_highlighted": True}
    else:
        return {"is_starred": True}



class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16) # When this gets used for anything besides flashing messages, change to be persistent

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
    assert os.path.exists(config['db']['host']), f"SQLite database file not found at {config['db']['host']}"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{config['db']['host']}?mode=ro"
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
    inspection = sqlalchemy.inspect(db.engine)
    print("Tables:", inspection.get_table_names())


# Photo Model
class Photos(db.Model):
    __table__ = db.metadata.tables["photos"]

class SizeVariants(db.Model):
    __table__ = db.metadata.tables["size_variants"]

class Albums(db.Model):
    __table__ = db.metadata.tables["base_albums"]

class Configs(db.Model):
    __table__ = db.metadata.tables["configs"]

@app.route('/')
def index():
    lychee_version_raw = db.session.execute(db.select(Configs).filter_by(key='version')).scalar().value
    lychee_version = get_lychee_version(lychee_version_raw)

    starred_filter_dict = get_highlighted_filter(**lychee_version)
    starred_photo_results = db.session.execute(db.select(Photos).filter_by(**starred_filter_dict)).scalars()
    starred_photos = starred_photo_results.all()

    random_photo_results = random.choices(starred_photos, k=3)
    random_photos = []
    for photo in random_photo_results:
        photo_id = photo.id
        photo_title = photo.title
        if lychee_version['major'] < 6 or (lychee_version['major'] == 6 and (lychee_version['minor'] < 6) or (lychee_version['minor'] == 6 and lychee_version['patch'] < 6)):
            # Lychee v6.6.6 "refactored the photo-album relation" https://github.com/LycheeOrg/Lychee/pull/3359
            album_id = photo.album_id
        elif "photo_album" in db.metadata.tables: # should be good for v6.6.6 and v7?
            class PhotoAlbum(db.Model):
                __table__ = db.metadata.tables["photo_album"]
            photo_album_result = db.session.execute(db.select(PhotoAlbum).filter_by(photo_id=photo_id)).scalar()
            if photo_album_result is not None:
                album_id = photo_album_result.album_id
        elif lychee_version['major'] < 7:
            # old_album_id was removed in the v7 refactoring, but still exists in v6.6.6 and later.
            flash(f"""
                Could not find album ID using the photo_album table. Falling back to old_album_id field.
                Please update or alert devs about this issue.
                  (For photo "{photo.title}" on Lychee version {lychee_version['major']}.{lychee_version['minor']}.{lychee_version['patch']})
            """, "warning")
            album_id = photo.old_album_id
        else:
            album_id = "starred"
            flash(f"""
                Could not find album ID. Using "starred" as a backup. This will be janky.
                  Please update or alert devs about this issue.
                  (For photo "{photo.title}" on Lychee version {lychee_version['major']}.{lychee_version['minor']}.{lychee_version['patch']})
            """, "warning")
        photo_gallery_link = f'{lychee_base_url}/gallery/{album_id}/{photo_id}'
        album_link = f'{lychee_base_url}/gallery/{album_id}'

        album = db.session.execute(db.select(Albums).filter_by(id=album_id)).scalar()
        if album is None:
            flash(f"""Could not find album title? This is a weird bug, alert the devs. 
                  (For photo \"{photo_title}\" on Lychee version {lychee_version['major']}.{lychee_version['minor']}.{lychee_version['patch']})
            """, "warning")
            album_title = 'Unknown?'
        else:
            album_title = album.title

        size_variant = db.session.execute(db.select(SizeVariants).filter_by(photo_id=photo_id, type=2)).scalar()
        if size_variant is None:
            size_variant = db.session.execute(db.select(SizeVariants).filter_by(photo_id=photo_id, type=0)).scalar_one()
        photo_raw_link = f'{lychee_base_url}/uploads/{size_variant.short_path}'

        random_photos.append({"gallery_link": photo_gallery_link, 
                              "raw_link": photo_raw_link,
                              "title": photo_title,
                              "album_title": album_title,
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