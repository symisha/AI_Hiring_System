import React, { useState } from "react";

const FormPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    const formData = new FormData(e.currentTarget);

    try {
      const res = await fetch("http://localhost:8000/submit", {
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

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">

        <div>
          <label className="block mb-1 font-medium">Name</label>
          <input
            name="name"
            type="text"
            required
            className="w-full p-2 border rounded"
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Email</label>
          <input
            name="email"
            type="email"
            required
            className="w-full p-2 border rounded"
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Phone number</label>
          <input
            name="phone"
            type="text"
            required
            className="w-full p-2 border rounded"
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Upload Resume</label>
          <input
            name="resume"
            type="file"
            required
            className="w-full"
          />
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
