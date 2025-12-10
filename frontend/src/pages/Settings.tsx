import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";


const Settings = () => {
  const [resumeWeight, setResumeWeight] = useState(30);
  const [assessmentWeight, setAssessmentWeight] = useState(40);
  const [interviewWeight, setInterviewWeight] = useState(30);
//   const [darkMode, setDarkMode] = useState(false);
  const [darkMode, setDarkMode] = useState(true);


  return (
    <div className="space-y-6">
      {/* <div>
        <h2 className="text-3xl font-bold">Settings</h2>
        <p className="text-muted-foreground mt-1">
          Manage account, preferences, appearance and scoring rules.
        </p>
      </div> */}

      {/* ---------------- Account  ---------------- */}
      <Card>
        <div className="p-6">
        <h2 className="text-3xl font-bold">Settings</h2>
        <p className="text-muted-foreground mt-1">
          Manage account, preferences, appearance and scoring rules.
        </p>
        
      </div>
        <CardHeader>
          <CardTitle className="text-lg">Account & Security</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Change Password</label>
              <Input type="password" placeholder="New password" />
            </div>

            {/* <div className="space-y-2">
              <label className="text-sm font-medium">Two-Factor Authentication</label>
              <Button variant="secondary" onClick={() => alert("2FA toggled")}>
                Manage 2FA
              </Button>
            </div> */}
          </div>
          <Separator />

          <Button onClick={() => alert("Saved")}>Save Password</Button>
        </CardContent>
      </Card>

      {/* ---------------- Weights  ---------------- */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">AI Scoring Weights</CardTitle>
          <p className="text-sm text-muted-foreground">
            Configure scoring algorithm. The weights must total 100%.
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            ["Resume Screening", resumeWeight, setResumeWeight],
            ["Assessment", assessmentWeight, setAssessmentWeight],
            ["AI Interview", interviewWeight, setInterviewWeight],
          ].map(([label, value, setter]: any, i) => (
            <div key={i} className="flex items-center gap-3">
              <label className="w-44 text-sm font-medium">{label} Weight</label>
              <Input
                value={String(value)}
                onChange={(e) => setter(Number(e.target.value))}
              />
              <span className="text-sm text-muted-foreground">%</span>
            </div>
          ))}

          <Separator />

          <Button onClick={() => alert("Saved")}>Save Preferences</Button>
        </CardContent>
      </Card>

      {/* ---------------- System  ---------------- */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">System Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Dark Mode</label>
            <Switch checked={darkMode} onCheckedChange={setDarkMode} />
          </div>


          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Timezone</label>
            <Input placeholder="Select timezone" className="max-w-xs" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;
