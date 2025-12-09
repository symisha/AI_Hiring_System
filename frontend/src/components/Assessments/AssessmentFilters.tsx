import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const AssessmentFilters = () => {
  const [search, setSearch] = useState("");

  return (
    <div className="rounded-2xl bg-card p-4">
      <h3 className="font-semibold mb-2">Filters & Search</h3>

      <div className="space-y-3">
        <div>
          <label className="text-sm">Candidate name / email</label>
          <Input value={search} onChange={(e) => setSearch((e.target as HTMLInputElement).value)} placeholder="Search" />
        </div>

        <div>
          <label className="text-sm">Status</label>
          <Input placeholder="Pending / Completed / Not Started" />
        </div>

        <div>
          <label className="text-sm">Score range</label>
          <div className="flex gap-2">
            <Input placeholder="min" />
            <Input placeholder="max" />
          </div>
        </div>

        <div className="flex gap-2">
          <Button onClick={() => alert('Apply filters')}>Apply</Button>
          <Button onClick={() => setSearch("")} className="bg-gray-200 text-black">Clear</Button>
        </div>
      </div>
    </div>
  );
};

export default AssessmentFilters;
