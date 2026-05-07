import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";

const AIInterviewOverview = ({ candidates }: any) => {
  const total = candidates.length;
  const shortlisted = candidates.filter((c: any) => c.interviewStatus === "Shortlisted").length;
  const rejected = candidates.filter((c: any) => c.interviewStatus === "Rejected").length;

  const parts = [
    { label: "Shortlisted", value: shortlisted, color: "#10b981" },
    { label: "Rejected", value: rejected, color: "#ef4444" },
  ];

  const avgAiScore = Math.round(candidates.filter((c: any) => c.aiScore != null).reduce((s: number, c: any) => s + (c.aiScore || 0), 0) / (candidates.filter((c:any)=>c.aiScore!=null).length || 1));
  const avgComm = Math.round(candidates.filter((c:any)=>c.communication!=null).reduce((s:number,c:any)=>s+(c.communication||0),0)/(candidates.filter((c:any)=>c.communication!=null).length||1));
  const avgConf = Math.round(candidates.filter((c:any)=>c.confidence!=null).reduce((s:number,c:any)=>s+(c.confidence||0),0)/(candidates.filter((c:any)=>c.confidence!=null).length||1));

  return (
    <div className="flex items-center justify-between gap-6">
      <div>
        <h3 className="text-lg font-semibold">AI Interview Overview</h3>
        <p className="text-sm text-muted-foreground">Snapshot of AI interview progress</p>

        <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
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

export default AIInterviewOverview;