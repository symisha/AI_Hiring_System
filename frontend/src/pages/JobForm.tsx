import React, { useState, useEffect } from "react";
import { Upload, FileText, Plus, Trash } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { jobFormSchema } from "@/lib/validationSchemas";

interface JobFormProps {
  token: string;
  editingJob?: any;
  onEditComplete?: () => void;
}

const JobForm: React.FC<JobFormProps> = ({ token, editingJob, onEditComplete }) => {
  const [message, setMessage] = useState("");
  const [applyLink, setApplyLink] = useState("");
  const [loading, setLoading] = useState(false);
  const [fields, setFields] = useState<Array<{ key: string; value: string }>>([
    { key: "", value: "" },
  ]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState("");

  // Initialize form with editing job data if available
  useEffect(() => {
    if (editingJob) {
      const initialFields: Array<{ key: string; value: string }> = [];
      if (editingJob.job_metadata && typeof editingJob.job_metadata === "object") {
        // Preserve insertion order using Object.keys which maintains order in modern JS
        Object.keys(editingJob.job_metadata).forEach((key) => {
          const value = editingJob.job_metadata[key];
          initialFields.push({
            key,
            value: typeof value === "string" ? value : JSON.stringify(value),
          });
        });
      }
      if (initialFields.length === 0) {
        initialFields.push({ key: "", value: "" });
      }
      setFields(initialFields);
    }
  }, [editingJob]);

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
  setApplyLink("");
    setValidationError("");

  const form = e.currentTarget;
  const title = (form.elements.namedItem("title") as HTMLInputElement).value;
  const description = (form.elements.namedItem("description") as HTMLTextAreaElement)?.value || "";

    // Validate static fields with Yup and dynamic metadata manually.
    try {
      await jobFormSchema.validate({ title, description }, { abortEarly: false });
    } catch (err: any) {
      setValidationError(err?.errors?.[0] || "Please check the form fields.");
      setLoading(false);
      return;
    }

    if (fields.every((f) => !f.key?.trim() || !f.value?.trim())) {
      setValidationError("Add at least one custom field with both key and value.");
      setLoading(false);
      return;
    }

    const hasIncompleteField = fields.some((f) => (f.key?.trim() && !f.value?.trim()) || (!f.key?.trim() && f.value?.trim()));
    if (hasIncompleteField) {
      setValidationError("Each custom field must include both name and value.");
    setLoading(false);
    return;
  }

  // 2. Build the JSON payload (Matches your Python JobCreate model)
  const payload = {
    title: title,
    short_description: description,
    metadata: buildMetadataObject()
  };

  try {
    // Determine endpoint and method based on whether we're editing or creating
    const isEditing = editingJob && editingJob.id;
    const endpoint = isEditing 
      ? `${import.meta.env.VITE_BACKEND_URL}/routes/edit-job/${editingJob.id}`
      : `${import.meta.env.VITE_BACKEND_URL}/services/upload-job`;
    const method = isEditing ? "PUT" : "POST";

    const res = await fetch(endpoint, {
      method: method,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (res.ok) {
      if (isEditing) {
        setMessage("Job updated successfully.");
        if (onEditComplete) {
          setTimeout(() => onEditComplete(), 1000);
        }
      } else {
        setMessage(data.message || "Job uploaded successfully.");
        setApplyLink(data.apply_link || "");
        setFields([{ key: "", value: "" }]);
        form.reset();
      }
    } else {
      setMessage(data.detail?.[0]?.msg || data.message || "Operation failed");
    }
  } catch (err: any) {
    console.error(err);
    setMessage(err?.message || "Operation failed");
  } finally {
    setLoading(false);
  }
  };
  const previewMetadata = () => {
    if (selectedFile) return null;
    const obj = buildMetadataObject();
    return <pre className="whitespace-pre-wrap bg-gray-50 p-3 rounded-md text-sm">{JSON.stringify(obj, null, 2)}</pre>;
  };

  const copyApplyLink = () => {
    if (!applyLink) return;
    if (navigator && (navigator as any).clipboard && (navigator as any).clipboard.writeText) {
      (navigator as any).clipboard.writeText(applyLink);
      alert("Apply link copied to clipboard");
      return;
    }
    window.prompt("Copy this link:", applyLink);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div>
            <div className="flex items-center gap-3">
              <FileText className="w-7 h-7 text-primary" />
              <CardTitle className="text-3xl font-bold">
                {editingJob ? "Edit Job Description" : "Upload Job Description"}
              </CardTitle>
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
            defaultValue={editingJob?.title || ""}
          />
          {validationError && <p className="text-xs text-red-500 mt-1">{validationError}</p>}
        </div>

        {/* Short description */}
        <div>
          <label className="text-sm font-medium mb-1">Short Description (optional)</label>
          <Textarea
            name="description"
            rows={3}
            placeholder="One-line summary of the role (optional)"
            defaultValue={editingJob?.short_description || ""}
          />
        </div>

       

        {/* Dynamic fields builder */}
        <div className="bg-gradient-to-br from-primary/5 to-secondary/5 border border-primary/20 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <label className="text-lg font-bold bg-gradient-primary bg-clip-text text-transparent">Job Requirements & Details</label>
              <p className="text-xs text-muted-foreground mt-2">Add custom fields to define key job requirements and qualifications</p>
            </div>
            <Button 
              type="button" 
              onClick={handleAddField} 
              className="flex items-center gap-2 text-sm bg-gradient-primary hover:opacity-90 text-white shadow-lg"
              size="sm"
            >
              <Plus className="w-4 h-4" /> Add Field
            </Button>
          </div>

          <div className="space-y-3">
            {fields.map((f, idx) => (
              <div 
                key={idx} 
                className="bg-card border border-primary/10 rounded-lg p-4 hover:border-primary/30 hover:shadow-md transition-all"
              >
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center shadow-sm">
                    <span className="text-sm font-bold text-white">{idx + 1}</span>
                  </div>
                  <div className="flex-grow space-y-3">
                    <Input
                      value={f.key}
                      onChange={(e) => handleFieldChange(idx, e.target.value, f.value)}
                      placeholder="Field name (e.g., required_skills, experience_level)"
                      className="text-sm border-primary/20 focus:border-primary/50 focus:ring-primary/30"
                    />
                    <Textarea
                      value={f.value}
                      onChange={(e) => handleFieldChange(idx, f.key, e.target.value)}
                      placeholder="Field value (JSON, CSV list, or text)"
                      className="text-sm resize-none border-primary/20 focus:border-primary/50 focus:ring-primary/30"
                      rows={3}
                    />
                  </div>
                  <button 
                    type="button" 
                    onClick={() => handleRemoveField(idx)} 
                    className="flex-shrink-0 mt-1 text-destructive/70 hover:text-destructive hover:bg-destructive/10 p-2 rounded-lg transition-all"
                  >
                    <Trash className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {fields.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              <FileText className="w-8 h-8 mx-auto mb-3 opacity-50" />
              <p className="text-sm">No fields added yet. Click "Add Field" to get started</p>
            </div>
          )}
        </div>

        {/* Preview */}
        {/* {previewMetadata()} */}

            {/* Submit Button */}
            <Button type="submit" disabled={loading} variant="hero" size="default" className="w-full justify-center">
              <Upload className="w-4 h-4" />
              {loading ? (editingJob ? "Updating..." : "Uploading...") : (editingJob ? "Update Job" : "Upload Job")}
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

      {applyLink && (
        <div className="mt-3 p-3 rounded-lg bg-indigo-50 text-gray-800 border border-indigo-200">
          <p className="font-medium">Apply link generated:</p>
          <a href={applyLink} target="_blank" rel="noreferrer" className="text-indigo-600 underline break-all">
            {applyLink}
          </a>
          <div className="mt-2">
            <Button type="button" onClick={copyApplyLink} className="bg-indigo-600/70 text-white hover:bg-indigo-600/90">
              Copy Link
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobForm;