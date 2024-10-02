import sys
from waitress import serve
from flask import request, redirect
import logging
from src.server import CameraApp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

host = '0.0.0.0'

camera_app = CameraApp()

logger.info("Starting server...")
serve(camera_app.app, host=host, port=8123)
logger.info("Server started.")
