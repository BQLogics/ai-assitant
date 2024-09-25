# from flask import Flask, render_template, Response, jsonify
# import cv2
# import base64
# from threading import Lock, Thread
# from speech_recognition import Recognizer, Microphone, UnknownValueError
# import openai
# from dotenv import load_dotenv
# import io
# from pyaudio import PyAudio, paInt16

# app = Flask(__name__)
# load_dotenv()

# # Webcam Stream class
# class WebcamStream:
#     def __init__(self):
#         self.stream = cv2.VideoCapture(0)
#         _, self.frame = self.stream.read()
#         self.running = False
#         self.lock = Lock()

#     def start(self):
#         if self.running:
#             return self

#         self.running = True
#         self.thread = Thread(target=self.update, args=())
#         self.thread.start()
#         return self

#     def update(self):
#         while self.running:
#             _, frame = self.stream.read()
#             with self.lock:
#                 self.frame = frame

#     def read(self, encode=False):
#         with self.lock:
#             frame = self.frame.copy()

#         if encode:
#             _, buffer = cv2.imencode(".jpeg", frame)
#             return base64.b64encode(buffer).decode('utf-8')

#         return frame

#     def stop(self):
#         self.running = False
#         if self.thread.is_alive():
#             self.thread.join()

#     def __exit__(self, exc_type, exc_value, exc_traceback):
#         self.stream.release()


# # Assistant for processing prompts
# class Assistant:
#     def __init__(self):
#         pass

#     def answer(self, prompt, image):
#         # Send the prompt and image to OpenAI's model (this would be expanded with real API calls)
#         response = "This is a mock response for prompt: " + prompt
#         return response


# # Initialize Webcam stream and Assistant
# webcam_stream = WebcamStream().start()
# assistant = Assistant()


# # Flask route to serve video feed
# @app.route('/video_feed')
# def video_feed():
#     def generate_frames():
#         while True:
#             frame = webcam_stream.read(encode=True)
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + base64.b64decode(frame) + b'\r\n')
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# # Flask route to handle the assistant's response
# @app.route('/get_response', methods=['POST'])
# def get_response():
#     recognizer = Recognizer()
#     microphone = Microphone()
#     with microphone as source:
#         recognizer.adjust_for_ambient_noise(source)
#         audio = recognizer.listen(source)

#     try:
#         prompt = recognizer.recognize_google(audio)
#         image = webcam_stream.read(encode=True)
#         response = assistant.answer(prompt, image)
#         return jsonify({"response": response})
#     except UnknownValueError:
#         return jsonify({"response": "Sorry, I could not understand the audio."})


# @app.route('/')
# def index():
#     return render_template('index.html')


# if __name__ == '__main__':
#     app.run(debug=True)

# from flask import Flask, render_template, Response
# import cv2

# app = Flask(__name__)

# # Initialize the webcam feed using OpenCV
# camera = cv2.VideoCapture(0)  # 0 indicates the default camera

# def generate_frames():
#     while True:
#         # Read frame from the webcam
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             # Encode frame as JPEG
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()

#             # Serve the frame as a JPEG image
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# # Route for the home page
# @app.route('/')
# def index():
#     return render_template('index.html')

# # Route for video feed
# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, render_template, Response
import cv2
from threading import Thread, Lock

app = Flask(__name__)

class WebcamStream:
    def __init__(self):
        self.stream = cv2.VideoCapture(0)  # Open the default webcam
        self.running = False
        self.lock = Lock()

    def start(self):
        if self.running:
            return self

        self.running = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.running:
            ret, frame = self.stream.read()
            if not ret:
                print("Failed to grab frame")
                continue

            # Lock the frame for safe access
            self.lock.acquire()
            self.frame = frame
            self.lock.release()

    def read(self):
        self.lock.acquire()
        frame = self.frame.copy()
        self.lock.release()
        return frame

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stream.release()

# Initialize webcam stream
webcam_stream = WebcamStream().start()

# Function to generate frames from the webcam
def generate_frames():
    while True:
        frame = webcam_stream.read()
        if frame is None:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)  # Encode frame as JPEG
            frame = buffer.tobytes()  # Convert to bytes
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Return as part of HTTP response

# Define routes
@app.route('/')
def index():
    return render_template('index.html')  # Render the main HTML page

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')  # Stream video feed

if __name__ == "__main__":
    app.run(debug=True)
    webcam_stream.stop()


