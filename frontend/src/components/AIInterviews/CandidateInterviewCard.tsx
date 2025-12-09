import { Button } from "@/components/ui/button";

const statusColor = (s: string) => {
  switch (s) {
    case "Completed": return "bg-green-100 text-green-700";
    case "In Progress": return "bg-blue-100 text-blue-700";
    case "Not Started": return "bg-red-100 text-red-700";
    default: return "bg-neutral-100 text-neutral-700";
  }
};

const CandidateInterviewCard = ({ candidate, onView }: any) => {
  return (
    <div className="p-4 rounded-lg border bg-background flex items-start justify-between">
      <div>
        <div className="flex items-center gap-4">
          <div className="rounded-full h-10 w-10 bg-muted flex items-center justify-center">{candidate.name.split(' ').map((n: string)=>n[0]).slice(0,2).join('')}</div>
          <div>
            <div className="font-semibold">{candidate.name}</div>
            <div className="text-sm text-muted-foreground">{candidate.email} • Score: {candidate.assessmentScore}</div>
          </div>
        </div>

        <div className="mt-2 text-sm">
          <div>Invited: {candidate.invitedDate}</div>
          <div>AI Score: {candidate.aiScore ?? 'N/A'}</div>
        </div>
      </div>

      <div className="flex flex-col items-end gap-2">
        <span className={`px-2 py-1 rounded text-xs ${statusColor(candidate.interviewStatus)}`}>{candidate.interviewStatus}</span>
        <div className="flex gap-2">
          <Button size="sm" onClick={() => onView(candidate)}>View</Button>
          {/* <Button size="sm" className="bg-indigo-600 text-white" onClick={() => alert('Download report')}>Download</Button> */}
        </div>
      </div>
    </div>
  );
};

export default CandidateInterviewCard;
