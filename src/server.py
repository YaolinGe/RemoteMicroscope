from flask import Flask, send_file, render_template, request, Response, redirect, url_for
from flask_cors import CORS
import cv2
import os

class CameraApp:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.BACKEND = cv2.CAP_MSMF
        self.DEFAULT_RESOLUTION = (3840, 2160)  # Example: 4K UHD
        self.setup_routes()

    def setup_routes(self):
        self.app.add_url_rule("/", "list_all_cameras", self.list_all_cameras)
        self.app.add_url_rule('/capture', 'capture_image', self.capture_image, methods=['POST'])
        self.app.add_url_rule('/video_feed/<int:camera_index>', 'video_feed', self.video_feed)
        self.app.add_url_rule('/save_image', 'save_image', self.save_image, methods=['POST'])

    def set_camera_resolution(self, cap, width, height):
        """ Set the resolution for the camera and ensure it actually sets """
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # Get the actual resolution from the camera after setting
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"Requested resolution: {width}x{height}")
        print(f"Actual resolution: {actual_width}x{actual_height}")
        
        return actual_width, actual_height

    def list_all_cameras(self):
        """ Render camera list with capture button in each camera section """
        cameras = []
        for i in range(2):  # Check the first two cameras (can be adjusted)
            try:
                cap = cv2.VideoCapture(i, self.BACKEND) 
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
                    cap.release()
            except Exception as e:
                print(f"Error accessing camera {i}: {e}")
                continue
        return render_template('camera.html', cameras=cameras)

    def capture_image(self):
        # Get the selected camera index
        camera_index = int(request.form.get('camera_index'))

        cap = cv2.VideoCapture(camera_index, self.BACKEND)

        if not cap.isOpened():
            return "Camera not found", 404

        # Set the camera to the highest default resolution
        width, height = self.DEFAULT_RESOLUTION
        actual_width, actual_height = self.set_camera_resolution(cap, width, height)

        # Fallback: Use actual resolution if it's different from the default one
        if (actual_width, actual_height) != (width, height):
            print(f"Warning: Desired resolution {width}x{height} not supported. Using {actual_width}x{actual_height} instead.")

        # Capture the image
        ret, frame = cap.read()

        # If the frame is not captured, inform the user
        if not ret or frame is None:
            cap.release()
            return "Failed to capture image. The camera might not support the selected resolution.", 500

        filename = os.path.join(os.getcwd(), 'src', 'static', 'images', f'camera_{camera_index}.jpg')
        cv2.imwrite(filename, frame)  # Save the captured image

        cap.release()

        return render_template('capture_success.html', camera_index=camera_index)

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
        """Video streaming route."""
        return Response(self.generate_frames(camera_index), mimetype='multipart/x-mixed-replace; boundary=frame')

    def save_image(self):
        camera_index = int(request.form.get('camera_index'))
        new_filename = request.form.get('filename')
        old_filepath = os.path.join(os.getcwd(), 'src', 'static', 'images', f'camera_{camera_index}.jpg')
        new_filepath = os.path.join(os.getcwd(), 'src', 'static', 'images', f'{new_filename}.jpg')

        if os.path.exists(old_filepath):
            os.rename(old_filepath, new_filepath)
            return render_template('save_success.html',new_filename=new_filename)
        else:
            return "Image not found", 404

    def run(self, debug: bool =False):
        self.app.run(host='0.0.0.0', port=5000, debug=debug)

if __name__ == '__main__':
    camera_app = CameraApp()
    camera_app.run(debug=True)
