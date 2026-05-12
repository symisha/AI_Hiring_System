import React, { useState } from 'react';
import { supabase } from '@/supabaseClient';
import { 
  Plus, 
  Trash2, 
  Wand2, 
  ArrowLeft, 
  BrainCircuit,
  Eye,
  Edit3
} from 'lucide-react';

interface CreateAssessmentProps {
  jobId: string | number | undefined;
  jobTitle: string | undefined;
  onSave: () => void;
}

const CreateAssessment: React.FC<CreateAssessmentProps> = ({ jobId, jobTitle, onSave }) => {
  const [questions, setQuestions] = useState<any[]>([]);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  
  // New States for Viewing Mode
  const [isViewing, setIsViewing] = useState(false);
  const [savedTest, setSavedTest] = useState<any[]>([]);
  const [loadingSaved, setLoadingSaved] = useState(false);

  const fetchSavedAssessment = async () => {
    if (!jobId) return;
    setLoadingSaved(true);
    try {
      const { data, error } = await supabase
        .from('jobs')
        .select('test')
        .eq('id', jobId)
        .single();

      if (error) throw error;
      setSavedTest(data.test || []);
      setIsViewing(true);
    } catch (err: any) {
      alert(`Failed to fetch test: ${err.message}`);
    } finally {
      setLoadingSaved(false);
    }
  };

  const generateAIQuestions = async () => {
    if (!jobId) return alert("No Job ID provided.");
    const token = localStorage.getItem("token");
    if (!token) return alert("Session expired.");

    setGenerating(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/routes/generate-test/${jobId}`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            "ngrok-skip-browser-warning": "true",
        },
        body: JSON.stringify({ role: jobTitle, num_questions: 3 })
      });
      const data = await response.json();
      if (!response.ok) throw new Error("Server failed to generate test.");
      const questionData = Array.isArray(data) ? data : (data.questions || []);
      setQuestions(questionData);
    } catch (err: any) {
      alert(`AI Generation failed: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const addQuestion = () => {
    const newQ = {
      id: Date.now(),
      function_name: 'new_function',
      question_text: 'Describe the problem...',
      difficulty: 'Medium',
      test_input: '[]',
      expected_output: ''
    };
    setQuestions([...questions, newQ]);
  };

  const removeQuestion = (id: number) => {
    setQuestions(questions.filter(q => q.id !== id));
  };

  const updateQuestion = (id: number, field: string, value: string) => {
    setQuestions(questions.map(q => q.id === id ? { ...q, [field]: value } : q));
  };

  const saveToDatabase = async () => {
    if (!jobId) return;
    setSaving(true);
    try {
      const { error } = await supabase
        .from('jobs') 
        .update({ test: questions })
        .eq('id', jobId);
      
      if (error) throw error;
      alert("Assessment saved and linked to job!");
      onSave(); 
    } catch (err: any) {
      alert(`Error saving: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mt-4 animate-in fade-in slide-in-from-bottom-4 duration-700 max-w-6xl mx-auto px-4 pb-20">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 bg-[#0f0f15]/60 p-6 rounded-3xl border border-white/10 backdrop-blur-xl">
        <div>
          <button onClick={onSave} className="flex items-center gap-2 text-slate-500 hover:text-purple-400 mb-2 transition-colors">
            <ArrowLeft size={18} /> Return to Dashboard
          </button>
          <h1 className="text-2xl font-bold text-white">
            {isViewing ? "Viewing" : "Create"} Assessment for <span className="text-purple-500">{jobTitle}</span>
          </h1>
        </div>
        
        <div className="flex gap-3">
            <button 
                onClick={isViewing ? () => setIsViewing(false) : fetchSavedAssessment}
                className="bg-white/5 hover:bg-white/10 text-white px-6 py-3 rounded-2xl font-bold border border-white/10 flex items-center gap-2 transition-all"
            >
                {loadingSaved ? "Loading..." : isViewing ? <><Edit3 size={18}/> Edit Mode</> : <><Eye size={18}/> View Assessment</>}
            </button>

            {!isViewing && (
                <button 
                    onClick={saveToDatabase}
                    disabled={questions.length === 0 || saving}
                    className="bg-purple-600 hover:bg-purple-500 text-white px-10 py-3 rounded-2xl font-bold shadow-lg shadow-purple-500/20 transition-all disabled:opacity-20"
                >
                    {saving ? "Saving..." : "Save Assessment"}
                </button>
            )}
        </div>
      </div>

      {!isViewing ? (
        <>
          {/* EDITOR VIEW */}
          <div className="bg-gradient-to-br from-purple-600/10 to-transparent border border-purple-500/20 p-8 rounded-[2.5rem] mb-10 relative overflow-hidden">
            <BrainCircuit className="absolute -right-10 -bottom-10 text-purple-500/5 w-64 h-64" />
            <div className="relative z-10">
              <h2 className="text-xl font-bold text-white mb-2">Smart Generation</h2>
              <p className="text-slate-400 mb-6 max-w-lg">Generate specific coding challenges based on job metadata.</p>
              <div className="flex gap-4">
                <button 
                  onClick={generateAIQuestions}
                  disabled={generating}
                  className="flex items-center gap-3 bg-white text-black px-6 py-3 rounded-xl font-black hover:bg-purple-400 transition-all active:scale-95 disabled:opacity-50"
                >
                  {generating ? "AI is Processing..." : <><Wand2 size={18} /> Generate 3 Challenges</>}
                </button>
                <button 
                  onClick={addQuestion}
                  className="flex items-center gap-2 bg-white/5 text-white px-6 py-3 rounded-xl font-bold hover:bg-white/10 transition-all border border-white/10"
                >
                  <Plus size={18} /> Manual Add
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            {questions.map((q, index) => (
              <div key={q.id || index} className="bg-[#0f0f15] border border-white/5 p-8 rounded-3xl hover:border-purple-500/30 transition-all relative group">
                <div className="flex justify-between items-start mb-6">
                  <div className="px-4 py-1 bg-purple-500/10 border border-purple-500/20 rounded-full text-purple-400 text-xs font-bold uppercase tracking-widest">
                    Question {index + 1} — {q.difficulty}
                  </div>
                  <button onClick={() => removeQuestion(q.id)} className="text-slate-600 hover:text-red-500 transition-colors">
                    <Trash2 size={20} />
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                   <input value={q.function_name} onChange={(e) => updateQuestion(q.id, 'function_name', e.target.value)} className="w-full bg-black/40 border border-white/5 p-4 rounded-xl text-purple-400 font-mono text-sm outline-none" placeholder="Function Name" />
                   <select value={q.difficulty} onChange={(e) => updateQuestion(q.id, 'difficulty', e.target.value)} className="w-full bg-black/40 border border-white/5 p-4 rounded-xl text-slate-400 text-sm outline-none">
                      <option value="Easy">Easy</option>
                      <option value="Medium">Medium</option>
                      <option value="Hard">Hard</option>
                   </select>
                </div>
                <textarea value={q.question_text} onChange={(e) => updateQuestion(q.id, 'question_text', e.target.value)} className="w-full bg-black/40 border border-white/5 p-4 rounded-xl text-slate-300 text-sm h-32 outline-none resize-none mb-6" placeholder="Problem Description" />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                   <input value={q.test_input} onChange={(e) => updateQuestion(q.id, 'test_input', e.target.value)} className="w-full bg-black/40 border border-white/5 p-4 rounded-xl text-emerald-400 font-mono text-xs outline-none" placeholder="Input" />
                   <input value={q.expected_output} onChange={(e) => updateQuestion(q.id, 'expected_output', e.target.value)} className="w-full bg-black/40 border border-white/5 p-4 rounded-xl text-orange-400 font-mono text-xs outline-none" placeholder="Output" />
                </div>
              </div>
            ))}
          </div>
        </>
      ) : (
        /* READ-ONLY VIEW */
        <div className="space-y-6 animate-in slide-in-from-top-4 duration-500">
            {savedTest.length > 0 ? savedTest.map((q, index) => (
                <div key={index} className="bg-white/5 border border-white/10 p-8 rounded-3xl">
                    <div className="flex justify-between items-center mb-4">
                        <span className="text-purple-400 font-bold text-sm tracking-widest uppercase">Challenge {index + 1}</span>
                        <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase ${q.difficulty === 'Hard' ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                            {q.difficulty}
                        </span>
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2 font-mono text-purple-300">{q.function_name}()</h3>
                    <p className="text-slate-300 text-sm leading-relaxed mb-6 bg-black/20 p-4 rounded-xl border border-white/5">{q.question_text}</p>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 bg-black/40 rounded-lg border border-white/5">
                            <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Sample Input</p>
                            <code className="text-emerald-400 text-xs">{q.test_input}</code>
                        </div>
                        <div className="p-3 bg-black/40 rounded-lg border border-white/5">
                            <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Expected Result</p>
                            <code className="text-orange-400 text-xs">{q.expected_output}</code>
                        </div>
                    </div>
                </div>
            )) : (
                <div className="text-center py-20 bg-[#0f0f15] rounded-3xl border border-dashed border-white/10">
                    <p className="text-slate-500">No assessment found for this job in the database.</p>
                </div>
            )}
        </div>
      )}
    </div>
  );
};

export default CreateAssessment;