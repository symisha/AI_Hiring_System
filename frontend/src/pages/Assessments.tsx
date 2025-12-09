import { useState } from "react";
import AssessmentJobHeader from "@/components/Assessments/AssessmentJobHeader";
import AssessmentOverview from "@/components/Assessments/AssessmentOverview.tsx";
import AssessmentFilters from "@/components/Assessments/AssessmentFilters.tsx";
import CandidateAssessmentList from "@/components/Assessments/CandidateAssessmentList.tsx";
import CandidateAssessmentDetail from "@/components/Assessments/CandidateAssessmentDetail.tsx";
import { Card } from "@/components/ui/card";

const mockCandidates = [
  {
    id: "a1",
    name: "Alice Johnson",
    email: "alice.j@example.com",
    invitedDate: "2025-12-01",
    // assessmentType: "AI-generated",
    assessmentId: "AS-101",
    status: "Completed",
    score: 87,
    resume: "/resumes/alice_johnson.pdf",
    notes: "Strong backend skills",
  },
  {
    id: "a2",
    name: "Brian Lee",
    email: "brian.lee@example.com",
    invitedDate: "2025-12-03",
    // assessmentType: "Manual",
    assessmentId: "AS-102",
    status: "Pending",
    score: null,
    resume: "/resumes/brian_lee.pdf",
    notes: "Awaiting submission",
  },
  {
    id: "a3",
    name: "Carmen Diaz",
    email: "carmen.d@example.com",
    invitedDate: "2025-12-05",
    // assessmentType: "AI-generated",
    assessmentId: "AS-101",
    status: "Not Started",
    score: null,
    resume: "/resumes/carmen_diaz.pdf",
    notes: "Follow up needed",
  },
];

const Assessments = ({ jobId, job }: { jobId?: string; job?: any } = {}) => {
  const [candidates] = useState(mockCandidates);
  const [selected, setSelected] = useState<any | null>(null);

  return (
    <div>
      <AssessmentJobHeader
        jobTitle={job?.title ?? (jobId ? `Job ${jobId}` : "Backend Developer")}
        jobId={job?.id ?? jobId}
        totalInvited={candidates.length}
        assessmentsPending={candidates.filter((c) => c.status === "Pending").length}
        assessmentsCompleted={candidates.filter((c) => c.status === "Completed").length}
        assessmentType="AI-generated"
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-6">
        <div className="lg:col-span-1">
          <AssessmentFilters />
        </div>

        <div className="lg:col-span-3">
          <Card className="p-4">
            <AssessmentOverview candidates={candidates} />

            <div className="mt-6">
              <CandidateAssessmentList candidates={candidates} onSelect={setSelected} />
            </div>
          </Card>
        </div>
      </div>

      {selected && (
        <CandidateAssessmentDetail candidate={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
};

export default Assessments;
