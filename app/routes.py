from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_required, login_user, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from app.models import User, Ground, Competition, Team, Team_Ground, WatchlistItem, Watchlist

#  instalise Flask Login 
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/teams', methods=['GET'])
def menu():
    teams = Team.query.all()
    return render_template('/teams.html', teams = teams)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your username and password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/add_to_watchlist', methods=['POST'])
@login_required
def add_to_watchlist():
    team_id = request.form.get('team_id')

    # Check if the team exists
    team = Team.query.get(team_id)
    if not team:
        flash('Invalid team selection', 'error')
        return redirect(url_for('menu'))
    
    # Get or create the user's watchlist
    watchlist = Watchlist.query.filter_by(user_id=current_user.id).first()
    if not watchlist:
        watchlist = Watchlist(user_id=current_user.id)
        db.session.add(watchlist)
        db.session.commit()  # Commit to get the watchlist ID

    # Check if the team is already in the watchlist
    watchlist_item = WatchlistItem.query.filter_by(watchlist_id=watchlist.id, team_id=team_id).first()
    if watchlist_item:
        flash('Team is already in your watchlist!', 'info')
    else:
        watchlist_item = WatchlistItem(watchlist_id=watchlist.id, team_id=team_id)
        db.session.add(watchlist_item)
        flash('Team added to Watchlist successfully!', 'success')
    
    db.session.commit()
    return redirect(url_for('menu'))

@app.route('/view_watchlist')
@login_required
def view_watchlist():
    watchlist = current_user.watchlist
    watchlist_items = WatchlistItem.query.filter_by(watchlist_id=watchlist.id).all() if watchlist else []
    return render_template('watchlist.html', watchlist_items=watchlist_items)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)


