import { useState } from "react";
import AIInterviewJobHeader from "@/components/AIInterviews/AIInterviewJobHeader";
import AIInterviewOverview from "@/components/AIInterviews/AIInterviewOverview.tsx";
import AIInterviewFilters from "@/components/AIInterviews/AIInterviewFilters.tsx";
import CandidateInterviewList from "@/components/AIInterviews/CandidateInterviewList.tsx";
import CandidateInterviewDetail from "@/components/AIInterviews/CandidateInterviewDetail.tsx";
import { Card } from "@/components/ui/card";

const mockCandidates = [
  {
    id: "i1",
    name: "Alice Johnson",
    email: "alice.j@example.com",
    assessmentScore: 87,
    invitedDate: "2025-12-06",
    interviewStatus: "Completed",
    aiScore: 88,
    communication: 85,
    confidence: 90,
    fitLabel: "Strong Fit",
    transcript: "/transcripts/alice_i1.txt",
    media: "/media/alice_i1.mp4",
  },
  {
    id: "i2",
    name: "Brian Lee",
    email: "brian.lee@example.com",
    assessmentScore: 78,
    invitedDate: "2025-12-07",
    interviewStatus: "In Progress",
    aiScore: 72,
    communication: 70,
    confidence: 75,
    fitLabel: "Moderate Fit",
    transcript: "/transcripts/brian_i2.txt",
    media: "/media/brian_i2.mp4",
  },
  {
    id: "i3",
    name: "Carmen Diaz",
    email: "carmen.d@example.com",
    assessmentScore: 60,
    invitedDate: "2025-12-08",
    interviewStatus: "Not Started",
    aiScore: null,
    communication: null,
    confidence: null,
    fitLabel: "Weak Fit",
    transcript: null,
    media: null,
  },
];

const AIInterviews = ({ jobId, job }: { jobId?: string; job?: any } = {}) => {
  const [candidates] = useState(mockCandidates);
  const [selected, setSelected] = useState<any | null>(null);

  return (
    <div>
      <AIInterviewJobHeader
        jobTitle={job?.title ?? (jobId ? `Job ${jobId}` : "Backend Developer")}
        jobId={job?.id ?? jobId}
        invitedCount={candidates.length}
        mode="Asynchronous AI"
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-6">
        <div className="lg:col-span-1">
          <AIInterviewFilters />
        </div>

        <div className="lg:col-span-3">
          <Card className="p-4">
            <AIInterviewOverview candidates={candidates} />

            <div className="mt-6">
              <CandidateInterviewList candidates={candidates} onSelect={setSelected} />
            </div>
          </Card>
        </div>
      </div>

      {selected && (
        <CandidateInterviewDetail candidate={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
};

export default AIInterviews;
