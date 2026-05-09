import { Button } from "@/components/ui/button";

const ReportsJobHeader = ({ jobTitle, jobId, totalEvaluated, topCandidates }: any) => {
  return (
    <div className="flex items-center justify-between bg-card rounded-2xl p-4">
      <div>
        <h1 className="text-2xl font-bold">{jobTitle}</h1>
        <p className="text-sm text-muted-foreground">Job ID: {jobId ?? "-"}</p>
        <div className="mt-2 flex gap-3 text-sm">
          <div>Total evaluated: <strong>{totalEvaluated}</strong></div>
        </div>
        <div className="mt-2 flex gap-2">
          {topCandidates?.map((c: any, i: number) => (
            <span key={c.id} className="px-2 py-1 rounded bg-indigo-100 text-indigo-700 text-sm">{i+1}. {c.name}</span>
          ))}
        </div>
      </div>

      {/* <div className="flex gap-2">
        <Button onClick={() => alert('Download full report')}>Download Full Report</Button>
        <Button onClick={() => alert('Download individual')} className="bg-indigo-600 text-white">Download Individual</Button>
      </div> */}
    </div>
  );
};

export default ReportsJobHeader;
