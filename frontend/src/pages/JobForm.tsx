import React, { useState } from "react";
import { Upload, FileText } from "lucide-react";

interface JobFormProps {
  token: string;
}

const JobForm: React.FC<JobFormProps> = ({ token }) => {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    const formData = new FormData(e.currentTarget);

    try {
      const res = await fetch("http://localhost:8000/upload-job", {
        method: "POST",
        body: formData,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();
      setMessage(data.message + (data.file_url ? ` URL: ${data.file_url}` : ""));
    } catch {
      setMessage("Upload failed");
    }

    setLoading(false);
  };

  return (
    <div className="max-w-xl mx-auto mt-14 bg-white shadow-lg rounded-2xl p-8 border border-gray-200">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <FileText className="w-7 h-7 text-indigo-600" />
          Upload Job Description
        </h2>
        <p className="text-gray-600 text-sm mt-1">
          Upload the JD JSON file to automatically process job requirements.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Job Title */}
        <div>
          <label className="block mb-1.5 font-medium text-gray-800">Job Title</label>
          <input
            name="title"
            type="text"
            required
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            placeholder="e.g. Senior Frontend Developer"
          />
        </div>

        {/* Upload File */}
        <div>
          <label className="block mb-1.5 font-medium text-gray-800">Upload JD JSON File</label>
          <input
            name="jd_file"
            type="file"
            accept=".json,application/json"
            required
            className="w-full text-sm border border-gray-300 rounded-lg p-2 file:bg-indigo-600 file:text-white file:border-0 file:px-4 file:py-2 file:rounded-lg file:mr-3 hover:file:bg-indigo-700 cursor-pointer"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-indigo-600 text-white py-3 rounded-lg text-lg font-medium flex justify-center items-center gap-2 
          hover:bg-indigo-700 transition-all shadow-md disabled:opacity-70"
        >
          <Upload className="w-5 h-5" />
          {loading ? "Uploading..." : "Upload Job"}
        </button>
      </form>

      {/* Message */}
      {message && (
        <p className="mt-5 p-3 rounded-lg bg-indigo-50 text-gray-800 border border-indigo-200">
          {message}
        </p>
      )}
    </div>
  );
};

export default JobForm;
