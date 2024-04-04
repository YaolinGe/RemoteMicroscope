from waitress import serve
import logging
from src.server import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Start the server
logger.info("Starting server...")
serve(app, host='0.0.0.0', port=5000)
logger.info("Server started.")

