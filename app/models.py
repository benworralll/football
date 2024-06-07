from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship


db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    watchlist = db.relationship('Watchlist', backref='user', uselist=False)

class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    formed = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Integer)

class Competition(db.Model):
    __tablename__ = 'Competition'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    format = db.Column(db.String(100), nullable=False)
    prize = db.Column(db.String(100), nullable=False)

class Ground(db.Model):
    __tablename__ = 'Ground'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

class Team_Ground(db.Model):
    __tablename__ = 'Team_Ground'
    tid = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('ground.id'), primary_key=True)

class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    items = db.relationship('WatchlistItem', backref='watchlist', lazy=True)


class WatchlistItem(db.Model):
    __tablename__ = 'watchlist_items'
    id = db.Column(db.Integer, primary_key=True)
    watchlist_id = db.Column(db.Integer, db.ForeignKey('watchlist.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team = db.relationship('Team', backref='watchlist_items')