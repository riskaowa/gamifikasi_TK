import os
from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    # DEBUG mode should be controlled by environment variable
    debug_mode = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']
    socketio.run(app, host='0.0.0.0', port=port, debug=debug_mode)
