import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const Profile = () => {
  const [name, setName] = useState("HR Manager");
  const [email, setEmail] = useState("hr@example.com");

  return (
    <div className="p-4">
      <h2 className="text-2xl font-semibold mb-4">Profile</h2>

      <Card className="p-4 mb-4">
        <div className="flex items-center gap-4">
          <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center">A</div>
          <div>
            <h3 className="font-semibold">{name}</h3>
            <p className="text-sm text-muted-foreground">{email}</p>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="text-sm">Full Name</label>
            <Input value={name} onChange={(e) => setName((e.target as HTMLInputElement).value)} />
          </div>
          <div>
            <label className="text-sm">Email</label>
            <Input value={email} onChange={(e) => setEmail((e.target as HTMLInputElement).value)} />
          </div>
        </div>
        <div className="mt-4 flex gap-2 justify-end">
          <Button onClick={() => alert('Profile updated')}>Save</Button>
        </div>
      </Card>
    </div>
  );
};

export default Profile;
