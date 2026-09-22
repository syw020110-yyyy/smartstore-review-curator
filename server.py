import http.server
import urllib.request
import urllib.parse
import json
import traceback
import os
import sys
import webbrowser

PORT = 8000
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/seoul-citydata'):
            try:
                parsed = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed.query)
                raw_area = params.get('area', ['북촌한옥마을'])[0]
                area = urllib.parse.unquote(raw_area)
                key = '6a706e626f7375683332484b4e6166'
                encoded_area = urllib.parse.quote(area)
                target_url = f'http://openapi.seoul.go.kr:8088/{key}/json/citydata/1/5/{encoded_area}'
                
                req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as res:
                    body = res.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                err_msg = json.dumps({'error': str(e), 'trace': traceback.format_exc()}).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(err_msg)
            return

        return super().do_GET()

if __name__ == '__main__':
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    server = http.server.ThreadingHTTPServer(('0.0.0.0', PORT), CustomHandler)
    print(f"LOCAL PROTECTOR Server running on http://localhost:{PORT}")
    if '--open' in sys.argv:
        webbrowser.open(f'http://localhost:{PORT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()

