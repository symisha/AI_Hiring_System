const CandidatesTable = ({ candidates }: any) => {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-3">All INTERVIEW_GRADED Candidates (Ranked)</h3>
      <div className="overflow-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-muted-foreground">
              <th className="pr-4 pb-2">Rank</th>
              <th className="pr-4 pb-2">Candidate</th>
              <th className="pr-4 pb-2">Resume</th>
              <th className="pr-4 pb-2">Assessment</th>
              <th className="pr-4 pb-2">Interview Score</th>
              <th className="pb-2">Label</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map((c: any, idx: number) => (
              <tr key={c.id} className={`border-t ${c.isTopCandidate ? 'border-l-2 border-l-green-500' : ''}` }>
                <td className="py-2 pr-4">{idx + 1}</td>
                <td className="py-2 pr-4">
                  <div className="font-medium">{c.name}</div>
                  <div className="text-xs text-muted-foreground">{c.email || c.applicant_id}</div>
                </td>
                <td className="py-2 pr-4">{c.resumeScore ?? '—'}</td>
                <td className="py-2 pr-4">{c.assessmentScore ?? '—'}</td>
                <td className="py-2 pr-4 font-semibold">{c.interviewScore ?? '—'}</td>
                <td className="py-2">
                  {c.isTopCandidate ? (
                    <span className="px-2 py-0.5 rounded text-xs bg-green-100 text-green-700 font-medium">Top Candidate</span>
                  ) : c.isShortlisted ? (
                    <span className="px-2 py-0.5 rounded text-xs bg-blue-100 text-blue-700">Shortlisted</span>
                  ) : (
                    <span className="px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-500">Below Threshold</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CandidatesTable;
