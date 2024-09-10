from app import create_app, socketio

# Create the Flask app instance
app = create_app()

# Run the app with SocketIO support
if __name__ == "__main__":
    socketio.run(app, debug=True)