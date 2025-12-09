import { Button } from "@/components/ui/button";

const AssessmentJobHeader = ({ jobTitle, jobId, totalInvited, assessmentsPending, assessmentsCompleted, assessmentType }: any) => {
  return (
    <div className="flex items-center justify-between bg-card rounded-2xl p-4">
      <div>
        <h1 className="text-2xl font-bold">{jobTitle}</h1>
        <p className="text-sm text-muted-foreground">Job ID: {jobId ?? "-"}</p>
        <div className="mt-2 flex gap-3 text-sm">
          <div>Total invited: <strong>{totalInvited}</strong></div>
          <div>Pending: <strong>{assessmentsPending}</strong></div>
          <div>Completed: <strong>{assessmentsCompleted}</strong></div>
          <div>Type: <strong>{assessmentType}</strong></div>
        </div>
      </div>

      {/* <div className="flex gap-2">
        <Button onClick={() => alert('Bulk invite')}>Bulk Invite</Button>
        <Button onClick={() => alert('Re-invite')} className="bg-indigo-600 text-white">Re-invite</Button>
      </div> */}
    </div>
  );
};

export default AssessmentJobHeader;
