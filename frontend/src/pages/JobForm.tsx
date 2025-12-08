import React, { useState } from "react";

const JobForm: React.FC = () => {
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
      });

      const data = await res.json();
      setMessage(data.message + (data.file_url ? ` URL: ${data.file_url}` : ""));
    } catch {
      setMessage("Upload failed");
    }

    setLoading(false);
  };

  return (
    <div className="max-w-lg mx-auto mt-10 p-6 border rounded shadow">
      <h2 className="text-2xl mb-4 font-semibold">Upload Job Description</h2>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="block mb-1 font-medium">Job Title</label>
          <input name="title" type="text" required className="w-full p-2 border rounded"/>
        </div>

        <div>
          <label className="block mb-1 font-medium">Job Description</label>
          <textarea name="description" required className="w-full p-2 border rounded"/>
        </div>

        <div>
          <label className="block mb-1 font-medium">Upload JD JSON File</label>
          <input name="jd_file" type="file" accept=".json,application/json" required className="w-full"/>
        </div>

        <button type="submit" disabled={loading} className="bg-blue-600 py-2 rounded text-white hover:bg-blue-700">
          {loading ? "Uploading..." : "Upload"}
        </button>
      </form>

      {message && <p className="mt-4 p-2 border rounded bg-gray-100">{message}</p>}
    </div>
  );
};

export default JobForm;
