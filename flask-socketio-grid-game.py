import random
import string

from flask import Flask, render_template, request
from flask_assets import Environment
from flask_socketio import SocketIO, emit, join_room, send

app = Flask(__name__)
socketio = SocketIO(app)

assets = Environment(app)

GRID_DIMENSIONS = (20, 10)

GRID = {}

users_connected = set()


@app.route('/')
def index():
    return render_template('index.html', grid_dimentions=GRID_DIMENSIONS)


def get_init_position():
    return tuple([random.choice(range(x)) + 1 for x in GRID_DIMENSIONS])


@socketio.on('join', namespace='/grid-game')
def on_join(msg):
    # Adding the user to the room to count on him
    user_id = request.sid
    users_connected.add(user_id)

    # Calculate the user_id, symbol and initial position
    symbol = random.choice(string.ascii_uppercase)
    init_position = get_init_position()
    payload = dict(userId=user_id, symbol=symbol, pos=init_position)

    # adding the new point to the grid
    GRID[user_id] = dict(pos=init_position, symbol=symbol)

    # Sent to the user the grid status
    send(dict(userId=user_id, gridDimension=GRID_DIMENSIONS))
    emit('grid_status', GRID)

    # Sent in broadcast the new user, the new symbol and the new position
    emit('user_position', payload, broadcast=True)

    # Send in broadcast the actual number of connected users
    emit('users_connected', len(users_connected), broadcast=True)


@socketio.on('movement', namespace='/grid-game')
def on_movement(data):
    # get the user_id
    user_id = request.sid

    # get get the actual position
    user_info = GRID.get(user_id)
    if user_info:
        actual_pos = user_info['pos']
        symbol = user_info['symbol']
    else:
        return

    # calculate the new position
    direction = data.get('direction')
    new_position = get_new_position(actual_pos, direction)

    # updating the grid with the new user position
    GRID[user_id] = dict(pos=new_position, symbol=symbol)

    # broadcast the movement of the user
    payload = dict(userId=user_id, symbol=symbol, pos=new_position)
    emit('user_position', payload, broadcast=True)


def get_new_position(position, direction):
    x, y = 0, 0
    if direction == 'up':
        x, y = 0, -1
    elif direction == 'down':
        x, y = 0, 1
    elif direction == 'left':
        x, y = -1, 0
    elif direction == 'right':
        x, y = 1, 0
    return max(min(position[0] + x, GRID_DIMENSIONS[0]), 1), max(min(position[1] + y, GRID_DIMENSIONS[1]), 1)


@socketio.on('disconnect', namespace='/grid-game')
def on_disconnect():
    # Removing the user from all the rooms where he is and broadcasting the new number
    user_id = request.sid
    users_connected.remove(user_id)

    # removing the position of the user on the GRID
    del GRID[user_id]

    # Notifying the rest of users that this one have left
    emit('user_position', dict(userId=user_id, remove=True), broadcast=True)

    # Sending the new number of users connected
    emit('users_connected', len(users_connected), broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
