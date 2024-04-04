from flask import Flask, send_file, render_template
from flask_cors import CORS
import cv2
from src.clean import clean

import os
import tempfile

clean()

app = Flask(__name__)
CORS(app)
# CORS(app, resources={r"/capture-image": {"origins": "http://yourClientOriginHere"}})  # if you want to restrict the origin

@app.route("/")
def list_all_cameras(): 
    """ List all available cameras with all detailed information fetched by cv2, they will be rendered using cameraInfo.html """
    cameras = []
    for i in range(2):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append({
                    'index': i,
                    'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    'fps': cap.get(cv2.CAP_PROP_FPS),
                    'fourcc': int(cap.get(cv2.CAP_PROP_FOURCC)),
                    'backend': cap.getBackendName(),
                    'is_opened': cap.isOpened()
                })
                ret, frame = cap.read()
                filename = os.path.join(os.getcwd(), 'src', 'static', 'images', f'camera_{i}.jpg')
                if ret:
                    cv2.imwrite(filename, frame)  # Save the captured image
                cap.release()  # Release the camera
                print("Camera released successfully")
        except Exception as e:
            continue
    return render_template('camera.html', cameras=cameras)

@app.route('/camera/<int:index>', methods=['GET'])
def capture_image(index):
    # Access the camera (0 is the default camera)
    cap = cv2.VideoCapture(index)

    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Camera not found", 404

    # Capture a single image
    ret, frame = cap.read()
    filename = os.path.join(os.getcwd(), 'src', 'static', 'images', f'camera_{index}.jpg')
    if ret:
        cv2.imwrite(filename, frame)  # Save the captured image

    cap.release()  # Release the camera

    return send_file(filename, mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
