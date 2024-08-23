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
    ground_id = request.form.get('ground_id')

    # Validate inputs
    if not team_id and not ground_id:
        flash('Invalid selection', 'error')
        return redirect(url_for('menu'))
    
    # Get or create the user's watchlist
    watchlist = Watchlist.query.filter_by(user_id=current_user.id).first()
    if not watchlist:
        watchlist = Watchlist(user_id=current_user.id)
        db.session.add(watchlist)
        db.session.commit()

    # Check if the team or ground is already in the watchlist
    watchlist_item = WatchlistItem.query.filter_by(
        watchlist_id=watchlist.id,
        team_id=team_id,
        ground_id=ground_id
    ).first()

    if watchlist_item:
        flash('Item is already in your watchlist!', 'info')
    else:
        watchlist_item = WatchlistItem(
            watchlist_id=watchlist.id,
            team_id=team_id if team_id else None,
            ground_id=ground_id if ground_id else None
        )
        db.session.add(watchlist_item)
        flash('Item added to Watchlist successfully!', 'success')

    db.session.commit()
    return redirect(url_for('menu'))

@app.route('/view_watchlist')
@login_required
def view_watchlist():
    watchlist = current_user.watchlist
    watchlist_items = WatchlistItem.query.filter_by(watchlist_id=watchlist.id).all() if watchlist else []
    return render_template('watchlist.html', watchlist_items=watchlist_items)

@app.route('/remove_from_watchlist/<int:item_id>', methods=['POST'])
@login_required
def remove_from_watchlist(item_id):
    watchlist_item = WatchlistItem.query.get(item_id)
    
    if not watchlist_item:
        flash('Item not found.', 'error')
        return redirect(url_for('view_watchlist'))
    
    print(f"Item found: {watchlist_item}")  # Debug line
    
    if watchlist_item.watchlist.user_id != current_user.id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('view_watchlist'))
    
    try:
        db.session.delete(watchlist_item)
        db.session.commit()
        flash('Item removed from watchlist.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing item: {str(e)}', 'error')
    
    return redirect(url_for('view_watchlist'))
@app.route('/grounds', methods=['GET'])
def grounds():
    sort_by = request.args.get('sort_by', 'name')  # Default sort by name
    if sort_by == 'name':
        grounds = Ground.query.order_by(Ground.name).all()
    elif sort_by == 'capacity':
        grounds = Ground.query.order_by(Ground.capacity.desc()).all()
    else:
        grounds = Ground.query.order_by(Ground.name).all()

    return render_template('grounds.html', grounds=grounds)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/team_ground')
def team_ground():
    teams = Team.query.all()  # Fetch all teams
    return render_template('team_ground.html', teams=teams)

if __name__ == '__main__':
    app.run(debug=True)


