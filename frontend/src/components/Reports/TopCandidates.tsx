const TopCandidates = ({ candidates }: any) => {
  if (!candidates || candidates.length === 0) {
    return (
      <div>
        <h3 className="text-lg font-semibold">Top Candidates</h3>
        <p className="mt-2 text-sm text-muted-foreground">No shortlisted candidates (score ≥ 80) found.</p>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-lg font-semibold">Top Candidates</h3>
      <p className="text-xs text-muted-foreground mb-3">Top 2 scorers with final score ≥ 80</p>
      <div className="mt-2 space-y-3">
        {candidates.map((c: any, idx: number) => (
          <div key={c.id} className="p-3 rounded border bg-background">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold">{idx + 1}. {c.name}</div>
                <div className="text-sm text-muted-foreground">{c.email || c.applicant_id}</div>
              </div>
              <div className="text-right">
                <div className="font-bold text-lg text-green-600">{c.interviewScore}/100</div>
                <div className="text-xs text-green-700">Shortlisted</div>
              </div>
            </div>
            <div className="mt-2 text-sm text-muted-foreground">
              Resume: {c.resumeScore ?? '—'}
              {c.assessmentScore != null && ` • Assessment: ${c.assessmentScore}`}
              {c.interviewScore != null && ` • Interview: ${c.interviewScore}`}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopCandidates;
