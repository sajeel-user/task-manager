export default function Stats({ stats }) {
  const pct = stats.total ? Math.round((stats.completed / stats.total) * 100) : 0;
  return (
    <div className="stats">
      <div className="ring" style={{ "--pct": pct }} aria-label={`${pct}% complete`}>
        <span>{pct}%</span>
      </div>
      <div className="stats-text">
        <strong>{stats.active}</strong> active
        <br />
        <strong>{stats.completed}</strong> done
      </div>
    </div>
  );
}
