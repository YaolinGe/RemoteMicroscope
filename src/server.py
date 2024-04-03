from flask import Flask, send_file, render_template
from flask_cors import CORS
import cv2
import os

app = Flask(__name__)
CORS(app)

# CORS(app, resources={r"/capture-image": {"origins": "http://yourClientOriginHere"}})


@app.route("/")
def list_all_cameras(): 
    """ List all available cameras with all detailed information fetched by cv2, they will be rendered using cameraInfo.html """
    camera_info = []
    for i in range(2):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            camera_info.append({
                'index': i,
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'fourcc': int(cap.get(cv2.CAP_PROP_FOURCC)),
                'backend': cap.getBackendName(),
                'is_opened': cap.isOpened()
            })
            cap.release()
    return render_template('cameraInfo.html', camera_info=camera_info)

@app.route('/capture-image', methods=['GET'])
def capture_image():
    # Access the camera (0 is the default camera)
    cap = cv2.VideoCapture(1)

    # Capture a single image
    ret, frame = cap.read()
    filename ='captured_image.jpg'
    if ret:
        cv2.imwrite(filename, frame)  # Save the captured image

    cap.release()  # Release the camera

    return send_file(filename, mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
