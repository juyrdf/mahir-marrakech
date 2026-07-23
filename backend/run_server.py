import uvicorn
import os
import sys

# Ensure the backend directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Prevent UnicodeEncodeError on Windows stdout with emojis
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

if __name__ == "__main__":
    print("🧞 Mahir Marrakech Server is starting...")
    print("📍 URL: http://localhost:8000")
    print("🛠️ Admin: http://localhost:8000/admin")
    print("📱 App: http://localhost:8000/app")
    
    import socket
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    port = 8000
    if is_port_in_use(port):
        print(f"⚠️ Port {port} is busy, trying 8001...")
        port = 8001

    print(f"🚀 Application starting on: http://localhost:{port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
