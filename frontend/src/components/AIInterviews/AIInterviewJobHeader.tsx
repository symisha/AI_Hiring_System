import { Button } from "@/components/ui/button";

const AIInterviewJobHeader = ({ jobTitle, jobId, invitedCount, mode }: any) => {
  return (
    <div className="flex items-center justify-between bg-card rounded-2xl p-4">
      <div>
        <h1 className="text-2xl font-bold">{jobTitle}</h1>
        <p className="text-sm text-muted-foreground">Job ID: {jobId ?? "-"}</p>
        <div className="mt-2 flex gap-3 text-sm">
          <div>Invited: <strong>{invitedCount}</strong></div>
          <div>Mode: <strong>{mode}</strong></div>
        </div>
      </div>

      {/* <div className="flex gap-2">
        <Button onClick={() => alert('Bulk invite')}>Bulk Invite</Button>
      </div> */}
    </div>
  );
};

export default AIInterviewJobHeader;
