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
        const d = `M ${x1} ${y1} A ${radius} ${radius} 0 ${large} 1 ${x2} ${y2} L ${cx} ${cy} Z`;

        return <path key={i} d={d} fill={p.color} opacity={0.95} />;
      })}
      <circle cx={cx} cy={cy} r={radius - 16} fill="transparent" />
    </svg>
  );
};

const AIInterviewOverview = ({ candidates }: any) => {
  const total = candidates.length;
  const completed = candidates.filter((c: any) => c.interviewStatus === "Completed").length;
  const inProgress = candidates.filter((c: any) => c.interviewStatus === "In Progress").length;
  const notStarted = candidates.filter((c: any) => c.interviewStatus === "Not Started").length;

  const parts = [
    { label: "Completed", value: completed, color: "#10b981" },
    { label: "In Progress", value: inProgress, color: "#3b82f6" },
    { label: "Not Started", value: notStarted, color: "#ef4444" },
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
          <div>Completed: <strong>{completed}</strong></div>
          <div>In Progress: <strong>{inProgress}</strong></div>
          <div>Not Started: <strong>{notStarted}</strong></div>
          <div>Avg AI Score: <strong>{avgAiScore}</strong></div>
          <div>Comm Avg: <strong>{avgComm}</strong> • Conf Avg: <strong>{avgConf}</strong></div>
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

export default AIInterviewOverview;
