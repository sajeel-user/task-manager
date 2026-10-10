import { useState } from "react";

const EMPTY = { title: "", description: "", priority: "medium", due_date: "" };

export default function TaskForm({ onAdd }) {
  const [form, setForm] = useState(EMPTY);
  const [showMore, setShowMore] = useState(false);
  const [saving, setSaving] = useState(false);

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) return;
    setSaving(true);
    const ok = await onAdd({ ...form, due_date: form.due_date || null });
    setSaving(false);
    if (ok) {
      setForm(EMPTY);
      setShowMore(false);
    }
  };

  return (
    <form className="task-form" onSubmit={submit}>
      <div className="row">
        <input
          className="title-input"
          placeholder="What needs to be done?"
          value={form.title}
          onChange={set("title")}
          maxLength={200}
          aria-label="Task title"
        />
        <button className="primary" type="submit" disabled={saving || !form.title.trim()}>
          {saving ? "Adding…" : "Add task"}
        </button>
      </div>

      <button type="button" className="link" onClick={() => setShowMore(!showMore)}>
        {showMore ? "Hide details" : "+ Add details (priority, due date, notes)"}
      </button>

      {showMore && (
        <div className="details">
          <label>
            Priority
            <select value={form.priority} onChange={set("priority")}>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          <label>
            Due date
            <input type="date" value={form.due_date} onChange={set("due_date")} />
          </label>
          <label className="wide">
            Notes
            <textarea rows={2} value={form.description} onChange={set("description")} />
          </label>
        </div>
      )}
    </form>
  );
}
