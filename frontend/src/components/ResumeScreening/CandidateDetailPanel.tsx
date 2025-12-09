import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const CandidateDetailPanel = ({ candidate, onClose }: any) => {
  return (
    <div className="fixed right-6 top-12 w-[720px] h-[80vh] bg-card rounded-2xl shadow-lg overflow-auto p-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-xl font-semibold">{candidate.name}</h3>
          <p className="text-sm text-muted-foreground">{candidate.email} • Applied: {candidate.appliedDate}</p>
        </div>

        <div className="flex gap-2">
          <Button onClick={() => alert('Shortlisted')}>Shortlist</Button>
          <Button onClick={() => alert('Rejected')} className="bg-red-600 text-white">Reject</Button>
          <Button onClick={onClose} className="bg-gray-200 text-black">Close</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        <div className="md:col-span-2">
          <Card className="p-2">
            <h4 className="font-semibold mb-2">Resume Preview</h4>
            <div className="h-[56vh] bg-muted">
              <iframe title="resume" src={candidate.resume} className="w-full h-full" />
            </div>
          </Card>
        </div>

        <div>
          <Card className="p-3">
            <h4 className="font-semibold">AI Analysis</h4>
            <div className="mt-2 text-sm space-y-2">
              <div><strong>AI Match Score:</strong> {candidate.aiScore}</div>
              <div><strong>Top skills:</strong> {candidate.skills.slice(0,5).join(', ')}</div>
              <div><strong>Education:</strong> {candidate.education}</div>
              <div><strong>Experience:</strong> {candidate.experience} yrs</div>
              <div><strong>Reasons:</strong>
                <ul className="list-disc ml-5 mt-1">
                  {candidate.reasons.map((r: string, i: number) => <li key={i}>{r}</li>)}
                </ul>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CandidateDetailPanel;
