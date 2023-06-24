import os
import psycopg2
from flask import Flask, render_template, request, redirect, session, url_for, flash
from dotenv import load_dotenv

load_dotenv()


def get_db_conn():
    conn = psycopg2.connect(
            host=os.environ['POSTGRES_SERVER'],
            database=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'])
    return conn


app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']  # set a secret key for session
# admin = Admin(app, template_mode='bootstrap3')
# admin.add_view(admin_view.WinnerView(name='Winners'))

@app.route('/')
def home(previous_winner=None):
    if 'players' not in session:
        return render_template('start_over.html')
    return render_template('index.html', players=session['players'], previous_winner=previous_winner)


@app.route('/update_score', methods=['POST'])
def update_score():
    winner = request.form['winner']
    points = int(request.form['points'])
    gin_points = request.form.get('gin_points')
    undercut_points = request.form.get('undercut_points')
    for player in session['players']:
        if player['name'] == winner:
            player['score'] += points
            if gin_points:
                player['score'] += 25
                player['num_gins'] += 1
            if undercut_points:
                player['score'] += 25
                player['num_undercuts'] += 1
            player['hands_won'] += 1
            session.modified = True
            if player['score'] >= 200:
                return redirect(url_for('game_over', winner=player['name'], score=player['score'],
                                        hands_won=player['hands_won'], num_gins=player['num_gins'],
                                        num_undercuts=player['num_undercuts']))
    return redirect(url_for('home', previous_winner=winner))


@app.route('/new_game', methods=['POST'])
def new_game():
    session.clear()
    session['players'] = []
    for i in range(4):
        player_name = request.form.get('player' + str(i + 1))
        if player_name:
            session['players'].append({'name': player_name, 'score': 0, 'hands_won': 0, 'num_gins': 0,
                                       'num_undercuts': 0, 'games_won': 0})
    if len(session['players']) < 2:
        flash('Please enter at least two player names.')
        return redirect(url_for('new_game'))
    return redirect(url_for('home'))


@app.route('/game_over')
def game_over():
    winner = request.args.get('winner')
    score = request.args.get('score')
    hands_won = request.args.get('hands_won')
    num_gins = request.args.get('num_gins')
    num_undercuts = request.args.get('num_undercuts')
    # Use the conn variable to execute queries
    conn = get_db_conn()
    cursor = conn.cursor()

    # Check if winner already exists in database
    cursor.execute("SELECT * FROM winner WHERE name = %s", (winner,))
    existing_winner = cursor.fetchone()

    if existing_winner:
        # Update existing winner record
        updated_score = existing_winner[2] + int(score)  # Add the existing score to the new score
        updated_hands_won = existing_winner[3] + int(hands_won)  # Add the existing hands_won to the new hands_won
        updated_num_gins = existing_winner[4] + int(num_gins)  # Add the existing num_gins to the new num_gins
        updated_num_undercuts = existing_winner[
                                    5] + int(num_undercuts)  # Add the existing num_undercuts to the new num_undercuts
        games_won = existing_winner[6] + 1
        cursor.execute(
            "UPDATE winner SET score = %s, hands_won = %s, num_gins = %s, num_undercuts = %s, games_won = %s "
            "WHERE name = %s",
            (updated_score, updated_hands_won, updated_num_gins, updated_num_undercuts, games_won, winner))
    else:
        # Insert new winner record
        games_won = 1
        cursor.execute("INSERT INTO winner (name, score, hands_won, num_gins, num_undercuts, games_won) "
                       "VALUES (%s, %s, %s, %s, %s, %s)",
                       (winner, score, hands_won, num_gins, num_undercuts, games_won))

    # Commit changes to database
    conn.commit()

    # Close the connection
    cursor.close()
    conn.close()

    session.clear()

    return render_template('game_over.html', winner=winner, score=score, hands_won=hands_won,
                           num_gins=num_gins, num_undercuts=num_undercuts)


@app.route('/start_over', methods=['GET', 'POST'])
def start_over():
    session.clear()
    return render_template('start_over.html')


@app.route('/game_stats', methods=['GET'])
def game_stats():
    sort_by = request.args.get('sort_by') or 'score'
    # Establish a connection to the database
    conn = get_db_conn()
    # Create a cursor to execute SQL statements
    cursor = conn.cursor()
    # Execute a SELECT statement to retrieve all rows from the winner table, ordered by the specified column
    cursor.execute(f"SELECT * FROM winner ORDER BY {sort_by} DESC LIMIT 10")
    # Fetch the result of the query
    winners = cursor.fetchall()
    # Close the cursor and the connection
    cursor.close()
    conn.close()
    # Render the game_stats.html template, passing the winners to the template
    return render_template('game_stats.html', winners=winners)


if __name__ == '__main__':
    app.run(debug=True)


