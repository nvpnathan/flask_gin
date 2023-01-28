import os
import psycopg2
from flask import Flask, render_template, request, redirect, session, url_for

conn = psycopg2.connect(
        host="localhost",
        database="gin_db",
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'])


app = Flask(__name__)
app.secret_key = 'mysecretkey'  # set a secret key for session


@app.route('/')
def home():
    if 'players' not in session:
        session['players'] = [{'name': 'player 1', 'score': 0, 'hands_won': 0, 'num_gins': 0},
                              {'name': 'player 2', 'score': 0, 'hands_won': 0, 'num_gins': 0}]
    return render_template('index.html', players=session['players'])


@app.route('/update_score', methods=['POST'])
def update_score():
    winner = request.form['winner']
    points = int(request.form['points'])
    bonus_points = request.form.get('bonus_points')
    for player in session['players']:
        if player['name'] == winner:
            player['score'] += points
            if bonus_points:
                player['score'] += 25
                player['num_gins'] += 1
            player['hands_won'] += 1
            session.modified = True
            if player['score'] >= 200:
                return redirect(url_for('game_over', winner=player['name'], score=player['score'],
                                        hands_won=player['hands_won'], num_gins=player['num_gins']))
    return redirect(url_for('home'))


@app.route('/new_game', methods=['POST'])
def new_game():
    session.clear()
    session['players'] = []
    for i in range(3):
        player_name = request.form['player' + str(i + 1)]
        session['players'].append({'name': player_name, 'score': 0, 'hands_won': 0, 'num_gins': 0})
    return redirect(url_for('home'))


@app.route('/game_over')
def game_over():
    winner = request.args.get('winner')
    score = request.args.get('score')
    hands_won = request.args.get('hands_won')
    num_gins = request.args.get('num_gins')
    # use the conn variable to execute queries
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (winner, score, hands_won, num_gins) VALUES (%s, %s, %s, %s)", (winner, score, hands_won, num_gins))
    conn.commit()

    # Close the connection
    cursor.close()
    conn.close()
    return render_template('game_over.html', winner=winner, score=score, hands_won=hands_won, num_gins=num_gins)


@app.route('/start_over', methods=['POST'])
def start_over():
    session.clear()
    return render_template('start_over.html')


@app.route('/game_stats', methods=['POST'])
def game_stats():
    # retrieve data for all sessions from the database
    sessions = retrieve_sessions_from_db()
    # initialize variables to keep track of overall statistics
    games_won = 0
    total_points = 0
    total_hands_won = 0
    total_num_gins = 0
    # iterate through sessions to calculate overall statistics
    for session in sessions:
        for player in session['players']:
            if player.score >= 100:
                games_won += 1
            total_points += player.score
            total_hands_won += player.hands_won
            total_num_gins += player.num_gins
    return render_template('game_stats.html', sessions=sessions)


if __name__ == '__main__':
    app.run(debug=True)


