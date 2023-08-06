from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from dotenv import load_dotenv
import base64
import os
import requests
from datetime import datetime
from prefect import task, Flow

from prefect.blocks.system import Secret


load_dotenv()

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
DB_PATH = "sqlite:///recently_played_songs.db"
# Endpoint to request an access token
TOKEN_URL = "https://accounts.spotify.com/api/token"

Base = declarative_base()


class RecentlyPlayedSong(Base):
    __tablename__ = "recently_played_songs"

    id = Column(Integer, primary_key=True)
    song_name = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String, nullable=False)
    played_at = Column(DateTime, nullable=False)


def create_engine_and_database():
    engine = create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    return engine


def create_session(engine):
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()


@task
def refresh_access_token(spotify_client_id, spotify_client_secret, refresh_token):
    auth_header = base64.b64encode(
        f"{spotify_client_id}:{spotify_client_secret}".encode()
    ).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = requests.post(TOKEN_URL, data=data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        access_token = data["access_token"]
        return access_token
    else:
        raise ValueError("Failed to refresh access token")


def get_latest_played_at():
    engine = create_engine_and_database()
    session = create_session(engine)

    # Retrieve the latest played_at timestamp from the database
    latest_played_at = session.query(func.max(RecentlyPlayedSong.played_at)).scalar()
    # convert to unix timestamp in millisecond. Required format for spotify API
    latest_played_at = int(latest_played_at.timestamp() * 1000)
    session.close()

    return latest_played_at


@task
def retrieve_songs_data(access_token, after):
    endpoint = "https://api.spotify.com/v1/me/player/recently-played"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    params = {
        "limit": 50,
        "after": after,
    }
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data


@task
def transform_and_insert_songs(songs_data):
    engine = create_engine_and_database()
    session = create_session(engine)

    for song in songs_data["items"]:
        track = song["track"]
        played_at = datetime.strptime(song["played_at"], "%Y-%m-%dT%H:%M:%S.%fZ")

        song_instance = RecentlyPlayedSong(
            song_name=track["name"],
            artist=track["album"]["artists"][0]["name"],
            album=track["album"]["name"],
            played_at=played_at,
        )
        session.add(song_instance)

    try:
        session.commit()
    except (IntegrityError, SQLAlchemyError) as e:
        session.rollback()
        raise ValueError(f"Error inserting data to the database: {str(e)}")
    finally:
        session.close()


@Flow
def recently_played_songs():
    # refresh_token = os.environ.get("SPOTIFY_REFRESH_TOKEN")
    refresh_token = Secret.load("spotify-refresh-token").get()
    spotify_client_id = Secret.load("spotify-client-id").get()
    spotify_client_secret = Secret.load("spotify-client-secret").get()

    # Set the initial timestamp for data retrieval (e.g., from the last processed record)
    after = get_latest_played_at()
    access_token = refresh_access_token(
        spotify_client_id, spotify_client_secret, refresh_token
    )
    songs_data = retrieve_songs_data(access_token, after)
    transform_and_insert_songs(songs_data)


if __name__ == "__main__":
    recently_played_songs()
