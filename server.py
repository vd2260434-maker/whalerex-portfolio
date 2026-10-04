import http.server
import socketserver
import os
import json
import hmac
import hashlib
import time
import base64
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get('PORT', 3000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
_jwt_env = os.environ.get('JWT_SECRET')
JWT_SECRET = _jwt_env.encode('utf-8') if _jwt_env else None

MESSAGES_FILE = os.path.join(BASE_DIR, '.local_messages.json')
SETTINGS_FILE = os.path.join(BASE_DIR, '.local_settings.json')

def base64url_encode(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def base64url_decode(s):
    padding = '=' * (4 - len(s) % 4)
    return base64.urlsafe_b64decode((s + padding).encode('utf-8')).decode('utf-8')

def create_token(payload):
    header = {"alg": "HS256", "typ": "JWT"}
    exp = int(time.time()) + 86400
    p = {**payload, "exp": exp}
    h_b64 = base64url_encode(json.dumps(header))
    p_b64 = base64url_encode(json.dumps(p))
    sig = hmac.new(JWT_SECRET, f"{h_b64}.{p_b64}".encode('utf-8'), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode('utf-8').rstrip('=')
    return f"{h_b64}.{p_b64}.{sig_b64}"

def verify_token(token):
    if not token or '.' not in token:
        return None
    parts = token.split('.')
    if len(parts) != 3:
        return None
    h_b64, p_b64, sig_b64 = parts
    expected_sig = hmac.new(JWT_SECRET, f"{h_b64}.{p_b64}".encode('utf-8'), hashlib.sha256).digest()
    expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode('utf-8').rstrip('=')
    if not hmac.compare_digest(sig_b64, expected_sig_b64):
        return None
    try:
        payload = json.loads(base64url_decode(p_b64))
        if payload.get('exp', 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None

def get_auth_token(headers):
    auth = headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth[7:].strip()
    cookie = headers.get('Cookie', '')
    for item in cookie.split(';'):
        if 'whalerex_token=' in item:
            return item.split('whalerex_token=')[1].strip()
    return None

def read_json_file(path, default):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return default

def write_json_file(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Error writing file:", e)

class WhalerexHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, status_code, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def parse_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length > 0:
            raw = self.rfile.read(length).decode('utf-8')
            try:
                return json.loads(raw)
            except Exception:
                return {}
        return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        # Rewrite /admin to /admin/index.html
        if path == '/admin' or path == '/admin/':
            self.path = '/admin/index.html'
            return super().do_GET()

        # API Auth check
        if path == '/api/auth':
            token = get_auth_token(self.headers)
            user = verify_token(token)
            if user:
                return self.send_json(200, {"authenticated": True, "user": user})
            return self.send_json(401, {"authenticated": False, "error": "Unauthorized"})

        # API Messages list
        if path == '/api/messages':
            token = get_auth_token(self.headers)
            if not verify_token(token):
                return self.send_json(401, {"error": "Unauthorized: Admin required"})
            messages = read_json_file(MESSAGES_FILE, [])
            return self.send_json(200, {"success": True, "count": len(messages), "messages": messages})

        # API Settings
        if path == '/api/settings':
            settings = read_json_file(SETTINGS_FILE, {
                "siteTitle": "Dinesh — Creative Web Developer & Designer",
                "brandName": "Whalerex",
                "availability": "Available for Freelance & Projects — Tamil Nadu, India",
                "contactEmail": "whalerex350@gmail.com",
                "featuredProject": {
                    "title": "Waffle House",
                    "tagline": "Artisanal Belgian Liege Boutique",
                    "liveUrl": "https://waffle-house-sigma.vercel.app/"
                }
            })
            return self.send_json(200, {"success": True, "settings": settings})

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        data = self.parse_body()

        # Login
        if path == '/api/login':
            if not ADMIN_USERNAME or not ADMIN_PASSWORD or not JWT_SECRET:
                return self.send_json(500, {"error": "Authentication environment variables not configured (ADMIN_USERNAME, ADMIN_PASSWORD, JWT_SECRET)"})
            username = data.get('username', '').strip()
            password = data.get('password', '')
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                token = create_token({"user": username, "role": "admin"})
                return self.send_json(200, {
                    "success": True,
                    "token": token,
                    "user": {"username": username, "role": "admin"}
                })
            return self.send_json(401, {"error": "Invalid username or password"})

        # Logout
        if path == '/api/logout':
            return self.send_json(200, {"success": True, "message": "Logged out"})

        # New Message (Public)
        if path == '/api/messages':
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            subject = data.get('subject', 'General Inquiry').strip()
            message = data.get('message', '').strip()

            if not name or not email or not message:
                return self.send_json(400, {"error": "Name, email, and message are required"})

            new_msg = {
                "id": f"msg_{int(time.time()*1000)}",
                "name": name[:100],
                "email": email[:150],
                "subject": subject[:200],
                "message": message[:3000],
                "status": "unread",
                "createdAt": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }

            messages = read_json_file(MESSAGES_FILE, [])
            messages.insert(0, new_msg)
            write_json_file(MESSAGES_FILE, messages)

            return self.send_json(201, {"success": True, "message": "Message received", "id": new_msg["id"]})

        # Settings update (Protected)
        if path == '/api/settings':
            token = get_auth_token(self.headers)
            if not verify_token(token):
                return self.send_json(401, {"error": "Unauthorized"})

            current = read_json_file(SETTINGS_FILE, {})
            current.update(data)
            current["updatedAt"] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            write_json_file(SETTINGS_FILE, current)
            return self.send_json(200, {"success": True, "settings": current})

        return self.send_json(404, {"error": "Not found"})

    def do_PATCH(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/api/messages':
            token = get_auth_token(self.headers)
            if not verify_token(token):
                return self.send_json(401, {"error": "Unauthorized"})

            data = self.parse_body()
            msg_id = data.get('id')
            status = data.get('status')
            messages = read_json_file(MESSAGES_FILE, [])
            for m in messages:
                if m.get('id') == msg_id:
                    m['status'] = status
                    write_json_file(MESSAGES_FILE, messages)
                    return self.send_json(200, {"success": True, "message": m})
            return self.send_json(404, {"error": "Message not found"})

        return self.send_json(404, {"error": "Not found"})

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/api/messages':
            token = get_auth_token(self.headers)
            if not verify_token(token):
                return self.send_json(401, {"error": "Unauthorized"})

            query = parse_qs(parsed.query)
            msg_id = query.get('id', [None])[0]
            if not msg_id:
                data = self.parse_body()
                msg_id = data.get('id')

            messages = read_json_file(MESSAGES_FILE, [])
            initial_len = len(messages)
            messages = [m for m in messages if m.get('id') != msg_id]
            if len(messages) == initial_len:
                return self.send_json(404, {"error": "Message not found"})

            write_json_file(MESSAGES_FILE, messages)
            return self.send_json(200, {"success": True, "message": "Deleted"})

        return self.send_json(404, {"error": "Not found"})

if __name__ == '__main__':
    os.chdir(BASE_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), WhalerexHandler) as httpd:
        print(f"Whalerex Full-Stack Server running at http://localhost:{PORT}")
        print(f"Admin Dashboard available at http://localhost:{PORT}/admin")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
