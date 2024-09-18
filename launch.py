import sys
from waitress import serve
import logging
from src.server import CameraApp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if the command-line argument is provided
# if len(sys.argv) > 1 and sys.argv[1] == 'server':
#     host = '0.0.0.0'
# else:
#     host = 'localhost'

host = '0.0.0.0'

# Instantiate the CameraApp class
camera_app = CameraApp()

# Start the server
logger.info("Starting server...")
serve(camera_app.app, host=host, port=8123)
logger.info("Server started.")
