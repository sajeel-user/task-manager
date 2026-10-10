# Task Manager

A full-stack to-do app with a **React** frontend and a **Python (Flask)** backend that stores tasks in **SQLite**.

## Features

- Add tasks with a priority (low / medium / high), due date and notes
- Mark tasks done, edit them inline, or delete them
- Filter by All / Active / Completed, and search by text
- Smart sorting: unfinished first, then by priority and due date
- "Due today", "Due tomorrow" and "Overdue" labels
- Progress ring showing how much you've completed
- Responsive layout with automatic dark mode

## Tech stack

| Part     | Tools                         |
| -------- | ----------------------------- |
| Frontend | React 18, Vite, plain CSS     |
| Backend  | Python 3, Flask, SQLite       |
| Tests    | Python `unittest`             |

## Project structure

```
task-manager/
├── backend/
│   ├── app.py            # Flask REST API
│   ├── test_app.py       # API tests
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── vite.config.js    # forwards /api calls to Flask in development
    └── src/
        ├── App.jsx
        ├── api.js        # fetch helpers for the API
        ├── styles.css
        └── components/
            ├── Stats.jsx
            ├── TaskForm.jsx
            └── TaskItem.jsx
```

## Getting started

You need **Python 3.9+** and **Node.js 18+** installed.

### 1. Start the backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate    macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The API runs at http://localhost:5000. The database file `tasks.db` is created automatically.

### 2. Start the frontend (in a second terminal)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

### Run the tests

```bash
cd backend
python -m unittest -v
```

## API reference

| Method | Endpoint                 | Description                                   |
| ------ | ------------------------ | --------------------------------------------- |
| GET    | `/api/tasks`             | List tasks. Query: `status` (all/active/completed), `q` (search) |
| POST   | `/api/tasks`             | Create a task (`title` required)              |
| GET    | `/api/tasks/<id>`        | Get one task                                  |
| PATCH  | `/api/tasks/<id>`        | Update any of: title, description, priority, due_date, completed |
| DELETE | `/api/tasks/<id>`        | Delete a task                                 |
| DELETE | `/api/tasks/completed`   | Delete all completed tasks                    |
| GET    | `/api/stats`             | Totals: `total`, `active`, `completed`        |

Example:

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "priority": "high", "due_date": "2026-10-15"}'
```

## Ideas for next steps

- User accounts and login
- Categories or tags
- Drag-and-drop reordering
- Deploy the backend (e.g. Render) and frontend (e.g. Vercel or Netlify)
