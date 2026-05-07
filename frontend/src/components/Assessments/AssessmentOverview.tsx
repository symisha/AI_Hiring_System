import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";

const AssessmentOverview = ({ candidates }: any) => {
  const total = candidates.length;
  const shortlisted = candidates.filter((c: any) => c.status === "Shortlisted").length;
  const rejected = candidates.filter((c: any) => c.status === "Rejected").length;

  const parts = [
    { label: "Shortlisted", value: shortlisted, color: "#10b981" },
    { label: "Rejected", value: rejected, color: "#ef4444" },
  ];

  const avgScore = candidates.filter((c: any) => c.score !== null && c.score !== undefined).reduce((s: number, c: any) => s + (c.score || 0), 0) / (candidates.filter((c: any) => c.score !== null && c.score !== undefined).length || 1);

  return (
    <div className="flex items-center justify-between gap-6">
      <div>
        <h3 className="text-lg font-semibold">Assessment Overview</h3>
        <p className="text-sm text-muted-foreground">Snapshot of assessment progress</p>

        <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
          <div>Total Candidates: <strong>{total}</strong></div>
          <div>Invited: <strong>{total}</strong></div>
          <div>Shortlisted: <strong>{shortlisted}</strong></div>
          <div>Rejected: <strong>{rejected}</strong></div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div style={{ width: 120, height: 120 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={parts} dataKey="value" nameKey="label" innerRadius={28} outerRadius={48} paddingAngle={4} isAnimationActive={true} animationDuration={800}>
                {parts.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
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

export default AssessmentOverview;