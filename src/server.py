from flask import Flask, send_file, render_template, request, Response, jsonify, redirect, url_for
from flask_cors import CORS
import cv2
import os
import base64
import asyncio
import time


class CameraApp:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.BACKEND = cv2.CAP_MSMF
        self.DEFAULT_RESOLUTION = (3840, 2160)
        self.camera_cache = {}
        self.camera_cache_time = 0
        self.CACHE_DURATION = 600
        self.initialize_app()

    def initialize_app(self):
        self.app.add_url_rule("/", "stream_camera", self.stream_camera, methods=['GET', 'POST'])
        self.app.add_url_rule('/capture', 'capture_image', self.capture_image, methods=['POST'])
        self.app.add_url_rule('/video_feed/<int:camera_index>', 'video_feed', self.video_feed)
        self.app.add_url_rule('/list_cameras', 'list_all_cameras_to_razor', self.list_all_cameras_to_razor, methods=['GET'])
        self.app.add_url_rule('/ping', 'ping', self.ping, methods=['GET'])
        self.ping(initialize=True)
        asyncio.run(self.initialize_cameras())

    async def initialize_cameras(self):
        cameras = await asyncio.gather(*(self.setup_camera(i) for i in range(2)))
        self.camera_cache = {i: camera for i, camera in enumerate(cameras) if camera is not None}
        self.camera_cache_time = time.time()

    async def setup_camera(self, index):
        try:
            cap = cv2.VideoCapture(index, self.BACKEND)
            if cap.isOpened():
                width, height = self.DEFAULT_RESOLUTION
                actual_width, actual_height = self.set_camera_resolution(cap, width, height)
                camera_info = {
                    'index': index,
                    'width': actual_width,
                    'height': actual_height,
                    'fps': cap.get(cv2.CAP_PROP_FPS),
                    'fourcc': int(cap.get(cv2.CAP_PROP_FOURCC)),
                    'backend': cap.getBackendName(),
                    'is_opened': cap.isOpened(),
                    'cap': cap
                }
                return camera_info
        except Exception as e:
            print(f"Error setting up camera {index}: {e}")
        return None

    def set_camera_resolution(self, cap, width, height):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera resolution set to: {actual_width}x{actual_height}")
        return actual_width, actual_height

    def ping(self, initialize=False):
        if not initialize:
            return "pong"

    def stream_camera(self):
        if request.method == 'POST':
            data = request.get_json()
            selected_camera = data.get('camera_index', 0)
        else:
            selected_camera = 0
        if selected_camera not in self.camera_cache:
            selected_camera = next(iter(self.camera_cache)) if self.camera_cache else 0
        return render_template('camera.html', cameras=self.camera_cache, selected_camera=selected_camera)

    def capture_image(self):
        camera_index = int(request.form.get('camera_index'))
        fileName = request.form.get('filename', 'camera_default')

        if camera_index not in self.camera_cache:
            return "Camera not found", 404

        cap = self.camera_cache[camera_index]['cap']
        ret, frame = cap.read()

        if not ret or frame is None:
            return "Failed to capture image.", 500

        filename = os.path.join(os.getcwd(), 'src', 'static', 'images', f'{fileName}.jpg')
        cv2.imwrite(filename, frame)

        _, buffer = cv2.imencode('.jpg', frame)
        base64_image = base64.b64encode(buffer).decode('utf-8')

        actual_width = self.camera_cache[camera_index]['width']
        actual_height = self.camera_cache[camera_index]['height']

        return jsonify({
            "message": "Image captured successfully",
            "fileName": f"{fileName}.jpg",
            "imageData": base64_image,
            "resolution": f"{actual_width}x{actual_height}"
        })

    async def list_all_cameras_to_razor(self):
        if time.time() - self.camera_cache_time > self.CACHE_DURATION:
            await self.initialize_cameras()
        return jsonify([{k: v for k, v in camera.items() if k != 'cap'} for camera in self.camera_cache.values()])

    async def check_camera(self, i, backend):
        try:
            cap = cv2.VideoCapture(i, backend)
            if cap.isOpened():
                camera_info = {
                    'index': i,
                    'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    'fps': cap.get(cv2.CAP_PROP_FPS),
                    'fourcc': int(cap.get(cv2.CAP_PROP_FOURCC)),
                    'backend': cap.getBackendName(),
                    'is_opened': cap.isOpened()
                }
                cap.release()
                return camera_info
        except Exception as e:
            print(f"Error accessing camera {i}: {e}")
        return None

    def generate_frames(self, camera_index):
        cap = cv2.VideoCapture(camera_index, self.BACKEND)

        if not cap.isOpened():
            return "Camera not found", 404

        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def video_feed(self, camera_index):
        return Response(self.generate_frames(camera_index), mimetype='multipart/x-mixed-replace; boundary=frame')

    def run(self, debug: bool = False):
        self.app.run(host='0.0.0.0', port=8123, debug=debug)


if __name__ == '__main__':
    camera_app = CameraApp()
    camera_app.run(debug=True)
