import React, { useState } from "react";
import { Upload, FileText, Plus, Trash } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

interface JobFormProps {
  token: string;
}

const JobForm: React.FC<JobFormProps> = ({ token }) => {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [fields, setFields] = useState<Array<{ key: string; value: string }>>([
    { key: "role_problem", value: "" },
  ]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleAddField = () => {
    setFields([...fields, { key: "", value: "" }]);
  };

  const handleRemoveField = (index: number) => {
    const next = fields.slice();
    next.splice(index, 1);
    setFields(next);
  };

  const handleFieldChange = (index: number, key: string, value: string) => {
    const next = fields.slice();
    next[index] = { key, value };
    setFields(next);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files && e.target.files[0];
    setSelectedFile(f || null);
  };

  const buildMetadataObject = () => {
    const obj: Record<string, any> = {};
    for (const f of fields) {
      if (!f.key) continue;
      // try parse value as JSON, else comma-split to array if contains comma, else raw string
      let val: any = f.value;
      try {
        val = JSON.parse(f.value);
      } catch {
        if (f.value.includes(",")) {
          val = f.value.split(",").map((s) => s.trim()).filter(Boolean);
        }
      }
      obj[f.key] = val;
    }
    return obj;
  };
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  setLoading(true);
  setMessage("");

  const form = e.currentTarget;
  const title = (form.elements.namedItem("title") as HTMLInputElement).value;
  const description = (form.elements.namedItem("description") as HTMLTextAreaElement)?.value || "";

  // 1. Validation
  if (fields.every((f) => !f.key || !f.value)) {
    setMessage("Add at least one custom field.");
    setLoading(false);
    return;
  }

  // 2. Build the JSON payload (Matches your Python JobCreate model)
  const payload = {
    title: title,
    short_description: description, // Mapping 'description' from form to 'short_description' in DB
    metadata: buildMetadataObject()
  };

  try {
    const res = await fetch(`${import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"}/services/upload-job`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json", // Crucial: Tells FastAPI to expect JSON
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload), // Send the object as a string
    });

    const data = await res.json();
    if (res.ok) {
      setMessage(data.message || "Job uploaded successfully.");
      setFields([{ key: "role_problem", value: "" }]);
      form.reset();
    } else {
      // This will show you exactly what field FastAPI is complaining about
      setMessage(data.detail?.[0]?.msg || data.message || "Upload failed");
    }
  } catch (err: any) {
    console.error(err);
    setMessage(err?.message || "Upload failed");
  } finally {
    setLoading(false);
  }
  };
  const previewMetadata = () => {
    if (selectedFile) return null;
    const obj = buildMetadataObject();
    return <pre className="whitespace-pre-wrap bg-gray-50 p-3 rounded-md text-sm">{JSON.stringify(obj, null, 2)}</pre>;
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div>
            <div className="flex items-center gap-3">
              <FileText className="w-7 h-7 text-primary" />
              <CardTitle className="text-3xl font-bold">Upload Job Description</CardTitle>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
        {/* Job Title */}
        <div>
          <label className="text-sm font-medium mb-1">Job Title</label>
          <Input
            name="title"
            type="text"
            required
            placeholder="e.g. Senior Frontend Developer"
          />
        </div>

        {/* Short description */}
        <div>
          <label className="text-sm font-medium mb-1">Short Description (optional)</label>
          <Textarea
            name="description"
            rows={3}
            placeholder="One-line summary of the role (optional)"
          />
        </div>

       

        {/* Dynamic fields builder */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium">Custom Fields</label>
            <button type="button" onClick={handleAddField} className="flex items-center gap-2 text-sm text-indigo-600">
              <Plus className="w-4 h-4" /> Add field
            </button>
          </div>

          <div className="space-y-2">
            {fields.map((f, idx) => (
              <div key={idx} className="grid grid-cols-12 gap-2 items-start">
                <Input
                  value={f.key}
                  onChange={(e) => handleFieldChange(idx, e.target.value, f.value)}
                  placeholder="field name (e.g. languages)"
                  className="col-span-4"
                />
                <Textarea
                  value={f.value}
                  onChange={(e) => handleFieldChange(idx, f.key, e.target.value)}
                  placeholder="value (JSON, CSV, or text)"
                  className="col-span-7"
                  rows={2}
                />
                <button type="button" onClick={() => handleRemoveField(idx)} className="col-span-1 text-red-500 p-2">
                  <Trash className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Preview */}
        {/* {previewMetadata()} */}

            {/* Submit Button */}
            <Button type="submit" disabled={loading} variant="hero" size="default" className="w-full justify-center">
              <Upload className="w-4 h-4" />
              {loading ? "Uploading..." : "Upload Job"}
            </Button>
          </form>
        </CardContent>
      </Card>

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