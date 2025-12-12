# Python UDP Signaling Server (STUN-lite)

A lightweight, standalone Signaling Server designed for P2P UDP Hole Punching. It maintains a registry of active peers using a local SQLite database and helps clients discover each other's Public IP and Port.

## 🚀 Features

* **Automatic DB Creation:** Creates `sqlitedb.db` on first run.
* **Persistent Storage:** Uses SQLite to store user sessions (Username, IP, Port, Last Seen).
* **Smart Updates:** Uses `UPSERT` logic (Insert or Update) to handle heartbeats efficiently.
* **Activity Sorting:** Returns peer lists sorted by "Seconds Ago" (most recently active users first).
* **Thread-Safe:** configured to handle SQLite connections in a simple single-threaded loop or compatible mode.

## 📋 Prerequisites

* **Python 3.6+** (Required for SQLite `ON CONFLICT` syntax support).
* A server with a **Public IP**.
* **UDP Port 3478** allowed in your firewall.

## ⚙️ Installation & Usage

1.  **Upload** the script to your server (e.g., `server.py`).
2.  **Run** the server:
    ```bash
    python3 server.py
    ```
    *The `sqlitedb.db` file will be created automatically.*

3.  **Keep it running** (Optional - using nohup):
    ```bash
    nohup python3 server.py &
    ```

## 🛠️ Communication Protocol

The server listens on **UDP 0.0.0.0:3478**.

### 1. Register / Heartbeat
Clients must send their username periodically (e.g., every 10-20 seconds) to stay on the list.
* **Request:** Raw string (e.g., `"MehmetTaha"`)
* **Server Action:** Updates IP, Port, and Timestamp in the database.

### 2. Get Peer List
Clients request the list of potential peers to connect with.
* **Request:** `"LIST"` (Case-insensitive)
* **Server Response:** A newline-separated CSV string.
    * **Format:** `username,ip,port,seconds_since_last_seen`
    * **Example:**
      ```text
      Ali,192.168.1.5,5454,0
      Ayse,203.0.113.10,6000,5
      Bob,198.51.100.2,4444,120
      ```

## 📂 Database Structure

The server creates a single table `users` in `sqlitedb.db`:

| Column | Type | Description |
| :--- | :--- | :--- |
| `username` | TEXT (PK) | Unique identifier for the peer. |
| `ip` | TEXT | The Public IP address seen by the server. |
| `port` | INTEGER | The Public Port seen by the server. |
| `last_seen` | INTEGER | Unix timestamp of the last heartbeat. |

## 🤝 Troubleshooting

* **"Database is locked" error:** This script is designed for low-concurrency. If you expand it to use multiple threads, you must handle SQLite locking carefully.
* **Clients can't connect:** Ensure your cloud provider (AWS/DigitalOcean/Azure) Security Groups allow **Inbound Custom UDP Rule** on port **3478**.
