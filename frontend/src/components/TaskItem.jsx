import { useState } from "react";

function dueLabel(due) {
  if (!due) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const date = new Date(`${due}T00:00:00`);
  const days = Math.round((date - today) / 86400000);
  if (days < 0) return { text: `Overdue · ${date.toLocaleDateString()}`, cls: "overdue" };
  if (days === 0) return { text: "Due today", cls: "soon" };
  if (days === 1) return { text: "Due tomorrow", cls: "soon" };
  return { text: `Due ${date.toLocaleDateString()}`, cls: "" };
}

export default function TaskItem({ task, onToggle, onSave, onDelete }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(task);

  const startEdit = () => {
    setDraft({ ...task, due_date: task.due_date || "" });
    setEditing(true);
  };

  const save = async (e) => {
    e.preventDefault();
    const ok = await onSave({
      title: draft.title,
      description: draft.description,
      priority: draft.priority,
      due_date: draft.due_date || null,
    });
    if (ok) setEditing(false);
  };

  if (editing) {
    const set = (field) => (e) => setDraft({ ...draft, [field]: e.target.value });
    return (
      <li className="task editing">
        <form onSubmit={save}>
          <input value={draft.title} onChange={set("title")} aria-label="Title" autoFocus />
          <textarea rows={2} value={draft.description} onChange={set("description")} aria-label="Notes" />
          <div className="row">
            <select value={draft.priority} onChange={set("priority")} aria-label="Priority">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
            <input type="date" value={draft.due_date} onChange={set("due_date")} aria-label="Due date" />
            <span className="spacer" />
            <button type="button" className="ghost" onClick={() => setEditing(false)}>Cancel</button>
            <button type="submit" className="primary">Save</button>
          </div>
        </form>
      </li>
    );
  }

  const due = !task.completed && dueLabel(task.due_date);

  return (
    <li className={`task ${task.completed ? "done" : ""}`}>
      <input
        type="checkbox"
        className="check"
        checked={task.completed}
        onChange={onToggle}
        aria-label={`Mark "${task.title}" as ${task.completed ? "not done" : "done"}`}
      />
      <div className="task-body">
        <div className="task-title">{task.title}</div>
        {task.description && <div className="task-desc">{task.description}</div>}
        <div className="meta">
          <span className={`badge ${task.priority}`}>{task.priority}</span>
          {due && <span className={`due ${due.cls}`}>{due.text}</span>}
        </div>
      </div>
      <div className="actions">
        <button className="ghost" onClick={startEdit} aria-label="Edit task">Edit</button>
        <button className="ghost danger" onClick={onDelete} aria-label="Delete task">Delete</button>
      </div>
    </li>
  );
}
