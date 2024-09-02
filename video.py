import cv2
import threading
import time
from flask import Flask, Response

app = Flask(__name__)

# Load your videos
video1 = cv2.VideoCapture('enter.mp4')
video2 = cv2.VideoCapture('exit.mp4')

# Global variables to hold the current frame
current_frame1 = None
current_frame2 = None

def loop_video(video, frame_holder):
    global current_frame1, current_frame2
    while True:
        success, frame = video.read()
        if not success:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        # Update the global frame holder with the current frame
        if frame_holder == 1:
            current_frame1 = frame
        else:
            current_frame2 = frame
        time.sleep(1/30)  # Adjust this for the correct frame rate

# Start background threads to loop the videos
threading.Thread(target=loop_video, args=(video1, 1)).start()
threading.Thread(target=loop_video, args=(video2, 2)).start()

def generate_frames(frame_holder):
    global current_frame1, current_frame2
    while True:
        # Use the latest frame from the video loop
        if frame_holder == 1:
            frame = current_frame1
        else:
            frame = current_frame2

        if frame is None:
            continue

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/camera1')
def camera1():
    return Response(generate_frames(1), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera2')
def camera2():
    return Response(generate_frames(2), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
