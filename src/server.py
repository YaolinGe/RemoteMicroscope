from flask import Flask, send_file
import cv2

app = Flask(__name__)

@app.route('/capture-image', methods=['GET'])
def capture_image():
    # Access the camera (0 is the default camera)
    cap = cv2.VideoCapture(0)

    # Capture a single image
    ret, frame = cap.read()
    filename = 'temp_image.jpg'
    if ret:
        cv2.imwrite(filename, frame)  # Save the captured image

    cap.release()  # Release the camera

    return send_file(filename, mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# from flask import Flask 

# app = Flask(__name__)

# @app.route("/")
# def hello_world(): 
#     return "<p>Hello, World!</p>"

