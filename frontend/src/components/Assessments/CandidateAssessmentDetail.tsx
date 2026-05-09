import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const CandidateAssessmentDetail = ({ candidate, onClose }: any) => {
  return (
    <div className="fixed right-6 top-12 w-[720px] h-[80vh] bg-card rounded-2xl shadow-lg overflow-auto p-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-xl font-semibold">{candidate.name}</h3>
          <p className="text-sm text-muted-foreground">{candidate.email} • Invited: {candidate.invitedDate}</p>
        </div>

        <div className="flex gap-2">
          <Button onClick={() => alert('Approve')}>Approve</Button>
          <Button onClick={onClose} className="bg-gray-200 text-black">Close</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        <div className="md:col-span-2">
          <Card className="p-2">
            <h4 className="font-semibold mb-2">Assessment Overview</h4>
            <div className="text-sm space-y-2">
              <div><strong>Type:</strong> {candidate.assessmentType}</div>
              <div><strong>Status:</strong> {candidate.status}</div>
              <div><strong>Score:</strong> {candidate.score ?? 'N/A'}</div>
            </div>

            <div className="mt-4">
              <h5 className="font-medium">Candidate responses</h5>
              <div className="mt-2 text-sm text-muted-foreground">(Responses preview would appear here)</div>
            </div>
          </Card>
        </div>

        {/* <div>
          <Card className="p-3">
            <h4 className="font-semibold">Analytics & Insights</h4>
            <div className="mt-2 text-sm space-y-2">
              <div><strong>Strong areas:</strong> Backend design</div>
              <div><strong>Weak areas:</strong> DevOps</div>
              <div><strong>Time taken:</strong> 32m</div>
            </div>
          </Card>
        </div> */}
      </div>
    </div>
  );
};

export default CandidateAssessmentDetail;
