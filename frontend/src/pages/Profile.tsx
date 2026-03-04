import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const Profile: React.FC = () => {
  // Company Basic Information
  const [companyName, setCompanyName] = useState("");
  const [companySize, setCompanySize] = useState("");
  const [website, setWebsite] = useState("");
  const [countryCity, setCountryCity] = useState("");
  const [companyDescription, setCompanyDescription] = useState("");

  // Primary Contact / Admin
  const [adminName, setAdminName] = useState("");
  const [designation, setDesignation] = useState("");
  const [adminEmail, setAdminEmail] = useState("");
  const [adminPhone, setAdminPhone] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!companyName) return alert("Company Name is required");
    if (!adminName || !adminEmail)
      return alert("Admin name and email are required");

    const fd = new FormData();
    fd.append("company_name", companyName);
    fd.append("company_size", companySize);
    fd.append("website", website);
    fd.append("country_city", countryCity);
    fd.append("company_description", companyDescription);

    fd.append("admin_name", adminName);
    fd.append("designation", designation);
    fd.append("admin_email", adminEmail);
    fd.append("admin_phone", adminPhone);

    try {
      const res = await fetch(
        import.meta.env.VITE_BACKEND_URL + "/company-profile",
        {
          method: "POST",
          body: fd,
        }
      );

      if (res.ok) {
        alert("Company profile saved");
      } else {
        const json = await res.json();
        alert(json.message || "Error saving profile");
      }
    } catch (err) {
      console.error(err);
      alert("Error saving profile");
    }
  };

  return (
    <form onSubmit={submit} className="space-y-6">
      {/* ================= Company Info ================= */}
      <Card className="p-8">
        <div className="p-2">
          <h2 className="text-3xl font-bold mb-4">
            Company Profile / Account Setup
          </h2>
        </div>

        <h3 className="font-medium mb-6">Company Basic Information</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm">Company Name</label>
            <Input
              value={companyName}
              onChange={(e) =>
                setCompanyName((e.target as HTMLInputElement).value)
              }
              required
            />
          </div>

          <div>
            <label className="text-sm">Company Size</label>
            <select
              value={companySize}
              onChange={(e) => setCompanySize(e.target.value)}
              className="w-full rounded-md bg-secondary border-border p-2"
            >
              <option value="">Select size</option>
              <option value="1-10">1–10</option>
              <option value="11-50">11–50</option>
              <option value="50-200">50–200</option>
              <option value=">200">200+</option>
            </select>
          </div>

          <div>
            <label className="text-sm">Website URL</label>
            <Input
              value={website}
              onChange={(e) =>
                setWebsite((e.target as HTMLInputElement).value)
              }
            />
          </div>

          <div>
            <label className="text-sm">Country / City</label>
            <Input
              value={countryCity}
              onChange={(e) =>
                setCountryCity((e.target as HTMLInputElement).value)
              }
            />
          </div>

          <div className="md:col-span-2">
            <label className="text-sm">Company Description</label>
            <textarea
              value={companyDescription}
              onChange={(e) => setCompanyDescription(e.target.value)}
              className="w-full rounded-md bg-secondary border-border p-2"
              rows={4}
            />
          </div>
        </div>
      </Card>

      {/* ================= Admin Info ================= */}
      <Card className="p-8">
        <h3 className="font-medium mb-6">
          Primary Contact Person (Admin)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm">Full Name</label>
            <Input
              value={adminName}
              onChange={(e) =>
                setAdminName((e.target as HTMLInputElement).value)
              }
              required
            />
          </div>

          <div>
            <label className="text-sm">Designation</label>
            <Input
              value={designation}
              onChange={(e) =>
                setDesignation((e.target as HTMLInputElement).value)
              }
            />
          </div>

          <div>
            <label className="text-sm">Work Email</label>
            <Input
              type="email"
              value={adminEmail}
              onChange={(e) =>
                setAdminEmail((e.target as HTMLInputElement).value)
              }
              required
            />
          </div>

          <div>
            <label className="text-sm">Phone Number</label>
            <Input
              value={adminPhone}
              onChange={(e) =>
                setAdminPhone((e.target as HTMLInputElement).value)
              }
            />
          </div>
        </div>

        <div className="mt-4 flex justify-end gap-2">
          <Button type="submit">Save Profile</Button>
        </div>
      </Card>
    </form>
  );
};

export default Profile;