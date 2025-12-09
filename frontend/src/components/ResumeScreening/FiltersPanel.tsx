import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const FiltersPanel = () => {
  const [skills, setSkills] = useState("");
  const [keywords, setKeywords] = useState("");

  return (
    <div className="rounded-2xl bg-card p-4">
      <h3 className="font-semibold mb-2">Search & Filters</h3>

      <div className="space-y-3">
        <div>
          <label className="text-sm">Skills</label>
          <Input value={skills} onChange={(e) => setSkills((e.target as HTMLInputElement).value)} placeholder="e.g. Node.js, Python" />
        </div>

        <div>
          <label className="text-sm">Experience (yrs)</label>
          <div className="flex gap-2">
            <Input placeholder="min" />
            <Input placeholder="max" />
          </div>
        </div>

        <div>
          <label className="text-sm">Education</label>
          <Input placeholder="B.Sc, M.Sc, PhD" />
        </div>

        <div>
          <label className="text-sm">Keywords</label>
          <Input value={keywords} onChange={(e) => setKeywords((e.target as HTMLInputElement).value)} placeholder="search text" />
        </div>

        <div className="flex gap-2">
          <Button onClick={() => alert('Apply filters')}>Apply</Button>
          <Button onClick={() => { setSkills(""); setKeywords(""); }} className="bg-gray-200 text-black">Clear</Button>
        </div>
      </div>
    </div>
  );
};

export default FiltersPanel;
