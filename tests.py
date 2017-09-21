from flask_socketio_grid_game import socketio, app


def test_connect():
    client = socketio.test_client(app, namespace='/grid-game')
    received = client.get_received('/grid-game')

    g = received[0].get
    assert g('name') == 'message'
    assert g('args').get('userId') is not None
    assert g('args').get('symbol') is not None
    assert all(isinstance(x, int) for x in g('args').get('gridDimension'))
    client.disconnect()


def test_user_move():
    namespace = '/grid-game'
    client = socketio.test_client(app, namespace=namespace)
    received = client.get_received(namespace)

    position_msg = [msg for msg in received if msg.get('name') == 'user_position'][-1]
    user_position = position_msg.get('args')[-1].get('pos')
    y_pos = user_position[1]
    client.emit('movement', {'direction': 'up'}, namespace=namespace)
    received = client.get_received(namespace)

    position_msg = [msg for msg in received if msg.get('name') == 'user_position'][-1]
    new_position = position_msg.get('args')[-1].get('pos')
    new_y_pos = new_position[1]

    # checking that the new position is correct having y + 1
    assert new_y_pos == (y_pos - 1)
    client.disconnect()
