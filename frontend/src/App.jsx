import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import TaskForm from "./components/TaskForm.jsx";
import TaskItem from "./components/TaskItem.jsx";
import Stats from "./components/Stats.jsx";

const FILTERS = [
  { key: "all", label: "All" },
  { key: "active", label: "Active" },
  { key: "completed", label: "Completed" },
];

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({ total: 0, completed: 0, active: 0 });
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    try {
      const [list, s] = await Promise.all([api.list({ status: filter, q: search }), api.stats()]);
      setTasks(list);
      setStats(s);
      setError("");
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Can't reach the server. Is the Flask backend running on port 5000?"
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }, [filter, search]);

  useEffect(() => {
    const t = setTimeout(refresh, 200); // small debounce for typing in search
    return () => clearTimeout(t);
  }, [refresh]);

  // Run an API action, then reload the list; show any error message.
  const run = async (action) => {
    try {
      await action();
      await refresh();
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Task Manager</h1>
          <p className="subtitle">Plan your day, one task at a time.</p>
        </div>
        <Stats stats={stats} />
      </header>

      <TaskForm onAdd={(task) => run(() => api.create(task))} />

      <div className="toolbar">
        <div className="filters" role="tablist">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              role="tab"
              aria-selected={filter === f.key}
              className={filter === f.key ? "chip active" : "chip"}
              onClick={() => setFilter(f.key)}
            >
              {f.label}
            </button>
          ))}
        </div>
        <input
          className="search"
          type="search"
          placeholder="Search tasks…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {error && (
        <div className="error" role="alert">
          {error}
          <button className="link" onClick={() => setError("")}>Dismiss</button>
        </div>
      )}

      {loading ? (
        <p className="empty">Loading…</p>
      ) : tasks.length === 0 ? (
        <p className="empty">
          {search || filter !== "all" ? "No tasks match." : "No tasks yet. Add your first one above!"}
        </p>
      ) : (
        <ul className="task-list">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onToggle={() => run(() => api.update(task.id, { completed: !task.completed }))}
              onSave={(fields) => run(() => api.update(task.id, fields))}
              onDelete={() => run(() => api.remove(task.id))}
            />
          ))}
        </ul>
      )}

      {stats.completed > 0 && (
        <div className="footer">
          <button className="link danger" onClick={() => run(api.clearCompleted)}>
            Clear {stats.completed} completed
          </button>
        </div>
      )}
    </div>
  );
}
