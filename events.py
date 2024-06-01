from flask_socketio import SocketIO
from flask import redirect, url_for

socketio = SocketIO()

@socketio.on("connect")
def handle_connect():
    print("Client connected!")
    
@socketio.on("user_join")
def handle_user_join(username):
    return redirect(url_for('views.other_page'))