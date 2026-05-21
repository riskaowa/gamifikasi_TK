from app import create_app, socketio
import webbrowser
import threading

app = create_app()

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    socketio.run(app, debug=True)
