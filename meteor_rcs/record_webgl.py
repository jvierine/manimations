"""Local render-preview server; accepts canvas recordings only into named movie assets."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT),**kw)
    def do_POST(self):
        name=self.path.removeprefix('/record/')
        if name not in {'do_height.mp4','do_height.webm','do_physical.mp4','do_physical.webm','fdtd_current.mp4','fdtd_current.webm','g_ion.mp4','g_ion.webm'}:
            self.send_error(400);return
        size=int(self.headers.get('Content-Length',0))
        if not 0<size<100_000_000:self.send_error(400);return
        (ROOT/'meteor_rcs/assets'/name).write_bytes(self.rfile.read(size))
        self.send_response(200);self.end_headers();self.wfile.write(b'Saved')
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',8769),Handler).serve_forever()
