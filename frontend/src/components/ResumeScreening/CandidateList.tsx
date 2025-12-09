import CandidateCard from "./CandidateCard";

const CandidateList = ({ candidates, onSelect }: any) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-lg font-semibold">Candidates</h4>
        <div className="text-sm text-muted-foreground">Showing {candidates.length}</div>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {candidates.map((c: any) => (
          <CandidateCard key={c.id} candidate={c} onView={onSelect} />
        ))}
      </div>
    </div>
  );
};

export default CandidateList;
