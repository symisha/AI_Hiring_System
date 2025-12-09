const CandidatesTable = ({ candidates }: any) => {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-3">All Candidates (Ranked)</h3>
      <div className="overflow-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left">
              <th className="pr-4">Rank</th>
              <th className="pr-4">Candidate</th>
              <th className="pr-4">Resume Match</th>
              <th className="pr-4">Assessment</th>
              <th className="pr-4">Interview</th>
              <th className="pr-4">Final Score</th>
              <th className="pr-4">Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map((c:any, idx:number) => (
              <tr key={c.id} className="border-t">
                <td className="py-2">{idx+1}</td>
                <td className="py-2">{c.name}<div className="text-muted-foreground text-xs">{c.email}</div></td>
                <td className="py-2">{c.resumeMatch}%</td>
                <td className="py-2">{c.assessment}</td>
                <td className="py-2">{c.interview}</td>
                <td className="py-2">{c.totalScore}</td>
                <td className="py-2">{c.recommendation}</td>
                <td className="py-2"><button onClick={() => alert('Download individual report') } className="text-sm text-blue-600">Download</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CandidatesTable;
