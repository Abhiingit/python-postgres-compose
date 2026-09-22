import os

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "appdb"),
        user=os.getenv("POSTGRES_USER", "appuser"),
        password=os.getenv("POSTGRES_PASSWORD", "apppassword"),
    )


@app.route("/")
def home():
    return "Python + PostgreSQL application is running!"


@app.route("/messages", methods=["GET"])
def get_messages():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS messages "
        "(id SERIAL PRIMARY KEY, message TEXT NOT NULL)"
    )

    cur.execute("SELECT id, message FROM messages ORDER BY id")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {"id": row[0], "message": row[1]}
        for row in rows
    ])


@app.route("/messages", methods=["POST"])
def add_message():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "message is required"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS messages "
        "(id SERIAL PRIMARY KEY, message TEXT NOT NULL)"
    )

    cur.execute(
        "INSERT INTO messages (message) VALUES (%s) RETURNING id",
        (data["message"],),
    )

    message_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "id": message_id,
        "message": data["message"]
    }), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)