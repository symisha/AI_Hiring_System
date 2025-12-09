import { Button } from "@/components/ui/button";

type Props = {
  jobTitle: string;
  applicationsCount: number;
};

const JobHeader = ({ jobTitle, applicationsCount }: Props) => {
  return (
    <div className="flex items-center justify-between bg-card rounded-2xl p-4">
      <div>
        <h1 className="text-2xl font-bold">{jobTitle}</h1>
        <p className="text-sm text-muted-foreground">{applicationsCount} applications</p>
        <div className="mt-2 flex gap-2 items-center">
          <span className="text-xs px-2 py-1 rounded bg-yellow-100 text-yellow-700">AI Screening: Running</span>
          <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-700">Auto Parse: Enabled</span>
        </div>
      </div>

      <div className="flex gap-2">
        <Button onClick={() => window.location.reload()}>Refresh</Button>
        <Button onClick={() => alert('Fetch new resumes')} className="bg-indigo-600 text-white">Fetch</Button>
      </div>
    </div>
  );
};

export default JobHeader;
