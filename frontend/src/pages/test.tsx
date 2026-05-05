import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import Editor from '@monaco-editor/react';

const AssessmentPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('ivt'); 
  
  const [questions, setQuestions] = useState<any[]>([]);
  const [solutions, setSolutions] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        // Using hardcoded URL to ensure connection during debugging
        const res = await fetch(`http://localhost:8000/services/get-test/${token}`);
        if (!res.ok) throw new Error("Failed to fetch assessment");
        
        const data = await res.json();
        setQuestions(data.questions || []);
      } catch (err) {
        console.error("Fetch error:", err);
        alert("Could not load assessment. Please check your connection or link.");
      } finally {
        setLoading(false);
      }
    };

    if (token) fetchQuestions();
    else setLoading(false);
  }, [token]);

  const handleSubmit = async () => {
    if (!token) return;
    setSubmitting(true);
    
    const payload = {
      token: token,
      solutions: Object.entries(solutions).map(([id, code]) => ({
        question_id: parseInt(id), 
        code: code
      }))
    };

    try {
      const res = await fetch(`http://localhost:8000/services/submit-test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        alert("Assessment Submitted Successfully!");
      } else {
        alert("Submission failed. Check your code for errors.");
      }
    } catch (err) {
      alert("Network error. Backend might be down.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="p-20 text-center text-xl">Loading Assessment...</div>;

  return (
    <div className="max-w-5xl mx-auto p-10 bg-white shadow-lg rounded-xl my-10">
      <h1 className="text-4xl font-extrabold mb-8 text-gray-800 border-b pb-4">Technical Challenge</h1>
      {questions.length === 0 ? (
        <p className="text-red-500">No questions found for this assessment.</p>
      ) : (
        questions.map((q, index) => (
          <div key={q.id} className="mb-12 p-6 bg-gray-50 rounded-lg border">
            <h3 className="text-xl font-bold mb-3 text-blue-600">Problem {index + 1}: {q.difficulty}</h3>
            <p className="text-gray-700 mb-6 bg-white p-4 rounded border-l-4 border-blue-400">
              {q.question_text}
            </p>
            <div className="border rounded-lg overflow-hidden shadow-sm">
              <Editor
                height="300px"
                defaultLanguage="python"
                theme="vs-dark"
                defaultValue={`def ${q.function_name}():\n    # Your code here\n    pass`}
                onChange={(value) => setSolutions({ ...solutions, [q.id]: value || '' })}
              />
            </div>
          </div>
        ))
      )}
      <button 
        onClick={handleSubmit} 
        disabled={submitting || questions.length === 0}
        className="w-full py-4 bg-blue-600 text-white text-xl font-bold rounded-xl hover:bg-blue-700 transition disabled:bg-gray-400"
      >
        {submitting ? "Processing Submission..." : "Finalize and Submit"}
      </button>
    </div>
  );
};

export default AssessmentPage;