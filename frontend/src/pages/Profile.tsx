import React from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { profileSchema } from "@/lib/validationSchemas";

type ProfileFormValues = {
  companyName: string;
  companySize: string;
  website: string | null;
  countryCity: string;
  companyDescription: string;
  adminName: string;
  designation: string;
  adminEmail: string;
  adminPhone: string | null;
};

const Profile: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormValues>({
    resolver: yupResolver(profileSchema),
    mode: "onChange",
    reValidateMode: "onChange",
    defaultValues: {
      companyName: "",
      companySize: "",
      website: "",
      countryCity: "",
      companyDescription: "",
      adminName: "",
      designation: "",
      adminEmail: "",
      adminPhone: "",
    },
  });

  const submit = async (values: ProfileFormValues) => {

    const fd = new FormData();
    fd.append("company_name", values.companyName);
    fd.append("company_size", values.companySize || "");
    fd.append("website", values.website || "");
    fd.append("country_city", values.countryCity || "");
    fd.append("company_description", values.companyDescription || "");

    fd.append("admin_name", values.adminName);
    fd.append("designation", values.designation || "");
    fd.append("admin_email", values.adminEmail);
    fd.append("admin_phone", values.adminPhone || "");

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
    <form onSubmit={handleSubmit(submit)} className="space-y-6">
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
              {...register("companyName")}
            />
            {errors.companyName && <p className="text-xs text-red-500 mt-1">{errors.companyName.message}</p>}
          </div>

          <div>
            <label className="text-sm">Company Size</label>
            <select
              {...register("companySize")}
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
              {...register("website")}
            />
            {errors.website && <p className="text-xs text-red-500 mt-1">{errors.website.message}</p>}
          </div>

          <div>
            <label className="text-sm">Country / City</label>
            <Input
              {...register("countryCity")}
            />
          </div>

          <div className="md:col-span-2">
            <label className="text-sm">Company Description</label>
            <textarea
              {...register("companyDescription")}
              className="w-full rounded-md bg-secondary border-border p-2"
              rows={4}
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="submit">Save Profile</Button>
        </div>
      </Card>

      {/* ================= Admin Info ================= */}
      {/* <Card className="p-8">
        <h3 className="font-medium mb-6">
          Primary Contact Person (Admin)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm">Full Name</label>
            <Input
              {...register("adminName")}
            />
            {errors.adminName && <p className="text-xs text-red-500 mt-1">{errors.adminName.message}</p>}
          </div>

          <div>
            <label className="text-sm">Designation</label>
            <Input
              {...register("designation")}
            />
          </div>

          <div>
            <label className="text-sm">Work Email</label>
            <Input
              type="email"
              {...register("adminEmail")}
            />
            {errors.adminEmail && <p className="text-xs text-red-500 mt-1">{errors.adminEmail.message}</p>}
          </div>

          <div>
            <label className="text-sm">Phone Number</label>
            <Input
              {...register("adminPhone")}
            />
            {errors.adminPhone && <p className="text-xs text-red-500 mt-1">{errors.adminPhone.message}</p>}
          </div>
        </div>

        <div className="mt-4 flex justify-end gap-2">
          <Button type="submit">Save Profile</Button>
        </div>
      </Card> */}
    </form>
  );
};

export default Profile;