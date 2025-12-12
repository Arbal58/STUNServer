import socket
import sqlite3
import time


conn = sqlite3.connect("sqlitedb.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    ip TEXT,
    port INTEGER,
    last_seen INTEGER
)
""")
conn.commit()


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 3478))
print("Server running on UDP port 3478...")


def handle_heartbeat(username, addr):

    if username.upper() == "LIST":
        return

    username = username.strip()
    ip = addr[0]
    port = addr[1]
    last_seen = int(time.time())

    sql = """
    INSERT INTO users(username, ip, port, last_seen)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(username) DO UPDATE SET
        ip = excluded.ip,
        port = excluded.port,
        last_seen = excluded.last_seen
    """
    cur.execute(sql, (username, ip, port, last_seen))
    conn.commit()

    print(f"[HB] Updated {username} → {ip}:{port}")


def handle_list_request(addr):
    """Send peer list as CSV with seconds_ago, sorted by recent activity"""
    cur.execute("SELECT username, ip, port, last_seen FROM users")
    rows = cur.fetchall()

    now = int(time.time())
    processed = []
    for username, ip, port, last_seen in rows:
        seconds_ago = max(0, now - last_seen) if last_seen else 999999
        processed.append((username, ip, port, seconds_ago))

    processed.sort(key=lambda x: x[3])

    csv_lines = [f"{u},{i},{p},{s}" for u, i, p, s in processed]
    csv_output = "\n".join(csv_lines)

    print(f"[LIST] Sent peer list ({len(processed)} users) to {addr}")
    sock.sendto(csv_output.encode(), addr)

while True:
    try:
        data, addr = sock.recvfrom(1024)
        message = data.decode(errors="ignore").strip()

        print(f"Received from {addr}: {message}")

        if message.upper() == "LIST":
            handle_list_request(addr)
        else:
            handle_heartbeat(message, addr)

    except KeyboardInterrupt:
        print("Shutting down server...")
        break
    except Exception as e:
        print(f"[ERROR] {e}")

conn.close()
sock.close()
 
