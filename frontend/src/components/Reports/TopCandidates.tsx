const TopCandidates = ({ candidates }: any) => {
  return (
    <div>
      <h3 className="text-lg font-semibold">Top Candidates</h3>
      <div className="mt-3 space-y-3">
        {candidates.map((c: any, idx: number) => (
          <div key={c.id} className="p-3 rounded border bg-background">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold">{idx+1}. {c.name}</div>
                <div className="text-sm text-muted-foreground">{c.email}</div>
              </div>
              <div className="text-right">
                <div className="font-bold text-lg">{c.totalScore}/100</div>
                <div className="text-sm">{c.recommendation}</div>
              </div>
            </div>

            <div className="mt-2 text-sm">
              <div>Assessment: {c.assessment} • Interview: {c.interview} • Resume: {c.resumeMatch}%</div>
              <div className="mt-1">Strengths: {c.strengths.join(', ')}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopCandidates;
