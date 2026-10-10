"""Task Manager API - a small Flask + SQLite REST backend."""

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone

from flask import Flask, g, jsonify, request

PRIORITIES = ("low", "medium", "high")


def create_app(db_path=None):
    app = Flask(__name__)
    app.config["DATABASE"] = db_path or os.environ.get(
        "TASKS_DB", os.path.join(os.path.dirname(__file__), "tasks.db")
    )

    # ---------- database helpers ----------

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        with closing(sqlite3.connect(app.config["DATABASE"])) as db, db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    priority TEXT NOT NULL DEFAULT 'medium',
                    due_date TEXT,
                    completed INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )

    init_db()

    def row_to_dict(row):
        task = dict(row)
        task["completed"] = bool(task["completed"])
        return task

    def error(message, status=400):
        return jsonify({"error": message}), status

    def validate(data, partial=False):
        """Return (clean_fields, error_message)."""
        clean = {}
        if "title" in data or not partial:
            title = str(data.get("title", "")).strip()
            if not title:
                return None, "Title is required."
            if len(title) > 200:
                return None, "Title must be 200 characters or fewer."
            clean["title"] = title
        if "description" in data:
            clean["description"] = str(data.get("description") or "").strip()
        if "priority" in data:
            if data["priority"] not in PRIORITIES:
                return None, f"Priority must be one of: {', '.join(PRIORITIES)}."
            clean["priority"] = data["priority"]
        if "due_date" in data:
            due = data.get("due_date") or None
            if due:
                try:
                    datetime.strptime(due, "%Y-%m-%d")
                except (TypeError, ValueError):
                    return None, "Due date must be in YYYY-MM-DD format."
            clean["due_date"] = due
        if "completed" in data:
            clean["completed"] = 1 if data["completed"] else 0
        return clean, None

    # ---------- CORS (so the React dev server can call the API) ----------

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
        return response

    # ---------- routes ----------

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/tasks")
    def list_tasks():
        status = request.args.get("status", "all")
        search = request.args.get("q", "").strip()
        sql = "SELECT * FROM tasks WHERE 1=1"
        params = []
        if status == "active":
            sql += " AND completed = 0"
        elif status == "completed":
            sql += " AND completed = 1"
        if search:
            sql += " AND (title LIKE ? OR description LIKE ?)"
            params += [f"%{search}%", f"%{search}%"]
        sql += (
            " ORDER BY completed ASC,"
            " CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END,"
            " due_date IS NULL, due_date ASC, id DESC"
        )
        rows = get_db().execute(sql, params).fetchall()
        return jsonify([row_to_dict(r) for r in rows])

    @app.post("/api/tasks")
    def create_task():
        data = request.get_json(silent=True) or {}
        clean, msg = validate(data)
        if msg:
            return error(msg)
        clean.setdefault("description", "")
        clean.setdefault("priority", "medium")
        clean.setdefault("due_date", None)
        clean.setdefault("completed", 0)
        clean["created_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        db = get_db()
        cols = ", ".join(clean)
        marks = ", ".join("?" for _ in clean)
        cur = db.execute(f"INSERT INTO tasks ({cols}) VALUES ({marks})", list(clean.values()))
        db.commit()
        row = db.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
        return jsonify(row_to_dict(row)), 201

    @app.get("/api/tasks/<int:task_id>")
    def get_task(task_id):
        row = get_db().execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            return error("Task not found.", 404)
        return jsonify(row_to_dict(row))

    @app.patch("/api/tasks/<int:task_id>")
    def update_task(task_id):
        db = get_db()
        if db.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,)).fetchone() is None:
            return error("Task not found.", 404)
        data = request.get_json(silent=True) or {}
        clean, msg = validate(data, partial=True)
        if msg:
            return error(msg)
        if clean:
            sets = ", ".join(f"{k} = ?" for k in clean)
            db.execute(f"UPDATE tasks SET {sets} WHERE id = ?", [*clean.values(), task_id])
            db.commit()
        row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return jsonify(row_to_dict(row))

    @app.delete("/api/tasks/<int:task_id>")
    def delete_task(task_id):
        db = get_db()
        cur = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        db.commit()
        if cur.rowcount == 0:
            return error("Task not found.", 404)
        return "", 204

    @app.delete("/api/tasks/completed")
    def clear_completed():
        db = get_db()
        cur = db.execute("DELETE FROM tasks WHERE completed = 1")
        db.commit()
        return jsonify({"deleted": cur.rowcount})

    @app.get("/api/stats")
    def stats():
        row = get_db().execute(
            "SELECT COUNT(*) AS total, COALESCE(SUM(completed), 0) AS completed FROM tasks"
        ).fetchone()
        total, done = row["total"], row["completed"]
        return jsonify({"total": total, "completed": done, "active": total - done})

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
