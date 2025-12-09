type Candidate = {
  id: string;
  status: string;
  aiScore: number;
};

const Donut = ({ parts }: { parts: { label: string; value: number; color: string }[] }) => {
  const total = parts.reduce((s, p) => s + p.value, 0) || 1;
  let angle = 0;
  const radius = 36;
  const cx = 40;
  const cy = 40;

  return (
    <svg width="120" height="120" viewBox="0 0 80 80">
      {parts.map((p, i) => {
        const frac = p.value / total;
        const start = angle;
        const end = angle + frac * Math.PI * 2;
        angle = end;

        const x1 = cx + radius * Math.cos(start - Math.PI / 2);
        const y1 = cy + radius * Math.sin(start - Math.PI / 2);
        const x2 = cx + radius * Math.cos(end - Math.PI / 2);
        const y2 = cy + radius * Math.sin(end - Math.PI / 2);
        const large = frac > 0.5 ? 1 : 0;
        // const d = `M ${cx} ${cy - radius} A ${radius} ${radius} 0 ${large} 1 ${x2} ${y2} L ${cx} ${cy} Z`;
        const d =`M ${x1} ${y1} A ${radius} ${radius} 0 ${large} 1 ${x2} ${y2} L ${cx} ${cy} Z`;

        return <path key={i} d={d} fill={p.color} opacity={0.95} />;
      })}
      <circle cx={cx} cy={cy} r={radius - 16} fill="transparent" />
    </svg>
  );
};

const ScreeningOverview = ({ candidates }: { candidates: Candidate[] }) => {
  const total = candidates.length;
  const statuses: Record<string, number> = {};
  candidates.forEach((c) => { statuses[c.status] = (statuses[c.status] || 0) + 1; });

  const parts = [
    { label: "New", value: statuses["New"] || 0, color: "#3b82f6" },
    { label: "Shortlisted", value: statuses["Shortlisted"] || 0, color: "#10b981" },
    { label: "Rejected", value: statuses["Rejected"] || 0, color: "#ef4444" },
    { label: "Review", value: statuses["Needs HR Review"] || 0, color: "#f59e0b" },
  ];

  const parsedCount = candidates.filter(c => c.aiScore !== undefined).length;
  const shortlisted = statuses["Shortlisted"] || 0;
  const rejected = statuses["Rejected"] || 0;
  const awaiting = statuses["Needs HR Review"] || 0;

  return (
    <div className="flex flex-col md:flex-row items-center justify-between gap-6">
      <div className="flex items-center gap-6">
        <div>
          <h3 className="text-lg font-semibold">AI Screening Overview</h3>
          <p className="text-sm text-muted-foreground">Quick glance of screening progress</p>

          <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
            <div>Total fetched: <span className="font-medium">{total}</span></div>
            <div>AI-parsed: <span className="font-medium">{parsedCount}</span></div>
            <div>Shortlisted: <span className="font-medium">{shortlisted}</span></div>
            <div>Rejected: <span className="font-medium">{rejected}</span></div>
            <div>Awaiting HR review: <span className="font-medium">{awaiting}</span></div>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <Donut parts={parts} />
        <div className="text-sm">
          {parts.map((p) => (
            <div key={p.label} className="flex items-center gap-2">
              <span className="w-3 h-3 rounded" style={{ background: p.color }} />
              <span>{p.label}: <strong>{p.value}</strong></span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ScreeningOverview;
