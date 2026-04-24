import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { resumeFormSchema } from "@/lib/validationSchemas";

type ResumeFormValues = {
  name: string;
  email: string;
  phone: string;
  resume: FileList;
};

const FormPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResumeFormValues>({
    resolver: yupResolver(resumeFormSchema),
    mode: "onChange",
    reValidateMode: "onChange",
  });

  const onSubmit = async (values: ResumeFormValues) => {
    setLoading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("name", values.name);
    formData.append("email", values.email);
    formData.append("phone", values.phone);
    if (values.resume && values.resume.length > 0) {
      formData.append("resume", values.resume[0]);
    }

    try {
      const res = await fetch("${import.meta.env.VITE_BACKEND_URL}/submit", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setMessage("Submitted successfully! Resume URL: " + data.resume_url);
    } catch (err) {
      setMessage("Submission failed!");
    }

    setLoading(false);
  };

  return (
    <div className="max-w-lg mx-auto mt-10 p-6 border rounded-lg shadow">
      <h2 className="text-2xl font-semibold mb-4">Submit Your Resume</h2>

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">

        <div>
          <label className="block mb-1 font-medium">Name</label>
          <input
            name="name"
            type="text"
            {...register("name")}
            className="w-full p-2 border rounded"
          />
          {errors.name && <p className="text-xs text-red-500 mt-1">{errors.name.message}</p>}
        </div>

        <div>
          <label className="block mb-1 font-medium">Email</label>
          <input
            name="email"
            type="email"
            {...register("email")}
            className="w-full p-2 border rounded"
          />
          {errors.email && <p className="text-xs text-red-500 mt-1">{errors.email.message}</p>}
        </div>

        <div>
          <label className="block mb-1 font-medium">Phone number</label>
          <input
            name="phone"
            type="text"
            {...register("phone")}
            className="w-full p-2 border rounded"
          />
          {errors.phone && <p className="text-xs text-red-500 mt-1">{errors.phone.message}</p>}
        </div>

        <div>
          <label className="block mb-1 font-medium">Upload Resume</label>
          <input
            name="resume"
            type="file"
            {...register("resume")}
            className="w-full"
          />
          {errors.resume && <p className="text-xs text-red-500 mt-1">{errors.resume.message as string}</p>}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
        >
          {loading ? "Submitting..." : "Submit"}
        </button>
      </form>

      {message && (
        <p className="mt-4 p-3 bg-gray-100 border rounded">{message}</p>
      )}
    </div>
  );
};

export default FormPage;
