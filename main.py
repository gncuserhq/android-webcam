from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import cv2
import threading
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import io

class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Android Camera Stream</h1><img src='/video_feed'>")
        elif self.path == '/video_feed':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            try:
                while True:
                    success, frame = CameraApp.camera.read()
                    if not success:
                        break
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()
                    self.wfile.write(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    time.sleep(0.1)
            except BrokenPipeError:
                pass

class CameraApp(App):
    camera = cv2.VideoCapture(0)
    
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.button = Button(text='Start Stream', on_press=self.start_stream)
        layout.add_widget(self.button)
        return layout

    def start_stream(self, instance):
        self.button.text = 'Streaming...'
        threading.Thread(target=self.run_server, daemon=True).start()
    
    def run_server(self):
        host_name = socket.gethostbyname(socket.gethostname())
        server_address = (host_name, 8080)
        httpd = HTTPServer(server_address, StreamingHandler)
        print(f"Streaming at http://{host_name}:8080")
        httpd.serve_forever()

if __name__ == '__main__':
    CameraApp().run()
