import { useState } from "react";
import ReportsJobHeader from "@/components/Reports/ReportsJobHeader";
import ReportsSummary from "@/components/Reports/ReportsSummary.tsx";
import TopCandidates from "@/components/Reports/TopCandidates.tsx";
import CandidatesTable from "@/components/Reports/CandidatesTable.tsx";
import { Card } from "@/components/ui/card";
import ReportsCharts from "@/components/Reports/ReportsCharts";

const mockCandidates = [
  { id: 'r1', name: 'Zara Ali', email: 'zara@example.com', assessment: 88, interview: 94, resumeMatch: 90, totalScore: 92, strengths: ['Communication','Python','Problem-solving'], recommendation: 'Strong' },
  { id: 'r2', name: 'Brian Lee', email: 'brian.lee@example.com', assessment: 78, interview: 72, resumeMatch: 80, totalScore: 76, strengths: ['Cloud','Microservices'], recommendation: 'Moderate' },
  { id: 'r3', name: 'Alice Johnson', email: 'alice.j@example.com', assessment: 87, interview: 88, resumeMatch: 85, totalScore: 87, strengths: ['Backend','Databases'], recommendation: 'Strong' },
  { id: 'r4', name: 'Carmen Diaz', email: 'carmen.d@example.com', assessment: 60, interview: 58, resumeMatch: 50, totalScore: 56, strengths: ['Frontend'], recommendation: 'Weak' },
];

const Reports = ({ jobId, job }: { jobId?: string; job?: any } = {}) => {
  const [candidates] = useState(mockCandidates);

  return (
    <div>
      <ReportsJobHeader
        jobTitle={job?.title ?? (jobId ? `Job ${jobId}` : 'Backend Developer')}
        jobId={job?.id ?? jobId}
        totalEvaluated={candidates.length}
        topCandidates={candidates.slice(0,3)}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        <div className="lg:col-span-2">
          <Card className="p-4 mb-6">
            <ReportsSummary candidates={candidates} />
          </Card>

          <Card className="p-4 mb-6">
            <TopCandidates candidates={candidates.slice(0,3)} />
          </Card>

          <Card className="p-4">
            <CandidatesTable candidates={candidates} />
          </Card>
        </div>

        <div>
          <Card className="p-4">
            <h3 className="text-lg font-semibold">Final Evaluation Graphs</h3>
            <div className="mt-4 text-sm text-muted-foreground">
              <ReportsCharts candidates={candidates} />
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Reports;
