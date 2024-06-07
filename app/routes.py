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


@app.route('/add_to_watchlist', methods=['POST'])
@login_required
def add_to_watchlist():
    team_id = request.form.get('team_id')

    team = Team.query.get(team_id)
    
    if not team:
        flash('Invalid team selection', 'error')
        return redirect(url_for('menu'))
    
    watchlist = current_user.watchlist
    if not watchlist:
        watchlist = watchlist(user_id=current_user.id)
        db.session.add(watchlist)
    
    watchlist_item = WatchlistItem.query.filter_by(watchlist_id=watchlist.id, team_id=team_id).first()
    
    if watchlist_item:
        watchlist_item.quantity += quantity
    else:
        watchlist_item = WatchlistItem(watchlist_id=watchlist.id, team_id=team_id)
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Team added to Watchlist successfully!', 'success')
    return redirect(url_for('menu'))



@app.route('/view_watchlist')
@login_required
def view_watchlist():
    watchlist = current_user.watchlist
    watchlist_items = WatchlistItem.query.filter_by(watchlist_id=watchlist.id).all() if watchlist else []
    return render_template('watchlist.html', cart_items=watchlist_items)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)


