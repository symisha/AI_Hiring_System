import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const CandidateInterviewDetail = ({ candidate, onClose }: any) => {
  return (
    <div className="fixed right-6 top-12 w-[780px] h-[80vh] bg-card rounded-2xl shadow-lg overflow-auto p-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-xl font-semibold">{candidate.name}</h3>
          <p className="text-sm text-muted-foreground">{candidate.email} • Invited: {candidate.invitedDate}</p>
        </div>

        <div className="flex gap-2">
          <Button onClick={() => alert('Shortlist')}>Shortlist</Button>
          <Button onClick={() => alert('Mark for final')} className="bg-indigo-600 text-white">Final Round</Button>
          <Button onClick={onClose} className="bg-gray-200 text-black">Close</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        <div className="md:col-span-2">
          <Card className="p-2">
            <h4 className="font-semibold mb-2">Interview Media / Transcript</h4>
            {candidate.media ? (
              <div className="h-64 bg-black">
                <video src={candidate.media} controls className="w-full h-full" />
              </div>
            ) : (
              <div className="h-64 bg-muted flex items-center justify-center text-sm">No media available</div>
            )}

            <div className="mt-4">
              <h5 className="font-medium">Transcript</h5>
              <div className="mt-2 text-sm text-muted-foreground">{candidate.transcript ? `Transcript available at ${candidate.transcript}` : "No transcript"}</div>
            </div>
          </Card>
        </div>

        <div>
          <Card className="p-3">
            <h4 className="font-semibold">AI Evaluation</h4>
            <div className="mt-2 text-sm space-y-2">
              <div><strong>AI Score:</strong> {candidate.aiScore ?? 'N/A'}</div>
              <div><strong>Communication:</strong> {candidate.communication ?? 'N/A'}</div>
              <div><strong>Confidence:</strong> {candidate.confidence ?? 'N/A'}</div>
              <div><strong>Fit:</strong> {candidate.fitLabel}</div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CandidateInterviewDetail;
