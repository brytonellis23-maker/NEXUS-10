import cv2, json, time, threading, socket
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

HOST="0.0.0.0"; PORT=8080
NANO_IP=""
camera=None
lock=threading.Lock()
state={"enabled":False,"pan":0,"tilt":90,"last_cmd":0,"nano":""}

def open_camera():
    global camera
    camera=cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    return camera.isOpened()

def frame_jpeg():
    global camera
    with lock:
        if camera is None and not open_camera(): return None
        ok, frame=camera.read()
    if not ok: return None
    ok, enc=cv2.imencode(".jpg",frame,[int(cv2.IMWRITE_JPEG_QUALITY),80])
    return enc.tobytes() if ok else None

class H(BaseHTTPRequestHandler):
    def cors(self):
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
    def json(self,obj,code=200):
        b=json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.cors(); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p=urlparse(self.path).path
        if p=="/api/state": self.json(state); return
        if p=="/stream":
            self.send_response(200); self.send_header("Content-Type","multipart/x-mixed-replace; boundary=frame"); self.send_header("Cache-Control","no-cache"); self.end_headers()
            while True:
                b=frame_jpeg()
                if not b: time.sleep(.2); continue
                try:
                    self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "+str(len(b)).encode()+b"\r\n\r\n"+b+b"\r\n")
                    self.wfile.flush()
                except Exception: break
            return
        super().do_GET()
    def do_POST(self):
        p=urlparse(self.path).path
        n=int(self.headers.get("Content-Length","0")); raw=self.rfile.read(n)
        try: d=json.loads(raw or b"{}")
        except: d={}
        if p=="/api/config":
            state["nano"]=str(d.get("nano","")).strip(); self.json(state); return
        if p=="/api/command":
            state["last_cmd"]=time.time()
            for k in ("enabled","pan","tilt"):
                if k in d: state[k]=d[k]
            # Forward command to Nano using stdlib HTTP. Nano IP is intentionally user-entered.
            ip=state.get("nano","")
            if ip:
                try:
                    import urllib.request
                    req=urllib.request.Request("http://"+ip+"/api/command",data=json.dumps(d).encode(),headers={"Content-Type":"application/json"},method="POST")
                    urllib.request.urlopen(req,timeout=.7).read()
                except Exception: pass
            self.json({"ok":True,"state":state}); return
        self.send_error(404)

if __name__=="__main__":
    print("NEXUS PC server: http://127.0.0.1:8080")
    print("Phone: use the PC's LAN IP, e.g. http://192.168.1.50:8080/mobile.html")
    if not open_camera(): print("WARNING: USB webcam was not found. Plug it in and restart the server.")
    ThreadingHTTPServer((HOST,PORT),H).serve_forever()
