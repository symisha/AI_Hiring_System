import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { ShieldCheck, AlertTriangle, Cpu, Lock } from 'lucide-react';
import { useSecurityShield } from '../hooks/useSecurityShield';

const AssessmentPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('ivt');
  
  const [questions, setQuestions] = useState<any[]>([]);
  const [solutions, setSolutions] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  // Initialize your security shield hook
  const { handleKeyDown } = useSecurityShield(token || 'unknown');

  // Helper to log violations to backend
  const reportViolation = useCallback(async (type: string) => {
    console.warn("Anti-cheat trigger:", type);
    try {
      await fetch(`http://localhost:8000/services/log-violation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, violation_type: type })
      });
    } catch (err) {
      console.error("Failed to log violation", err);
    }
  }, [token]);

  useEffect(() => {
    // 1. Detect Tab Switching
    const handleVisibility = () => {
      if (document.hidden) reportViolation("Tab/Window Switch Detected");
    };

    // 2. Detect Loss of Focus (Alt-Tab)
    const handleBlur = () => reportViolation("Alt-Tab Detected (Focus Lost)");

    // 3. Block Right Click Menu
    const handleContextMenu = (e: MouseEvent) => e.preventDefault();

    window.addEventListener("visibilitychange", handleVisibility);
    window.addEventListener("blur", handleBlur);
    window.addEventListener("contextmenu", handleContextMenu);

    return () => {
      window.removeEventListener("visibilitychange", handleVisibility);
      window.removeEventListener("blur", handleBlur);
      window.removeEventListener("contextmenu", handleContextMenu);
    };
  }, [reportViolation]);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const res = await fetch(`http://localhost:8000/services/get-test/${token}`);
        if (!res.ok) throw new Error("Failed to fetch assessment");
        const data = await res.json();
        setQuestions(data.questions || []);
      } catch (err) {
        console.error("Fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    if (token) fetchQuestions();
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
        alert("Submission failed. Check your connection.");
      }
    } catch (err) {
      alert("Network error.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return (
    <div className="h-screen flex items-center justify-center bg-[#050505]">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-purple-500"></div>
    </div>
  );

  return (
    <div className="min-h-screen py-12 px-4 md:px-8 relative overflow-hidden bg-[#050505] selection:bg-purple-500/30">
      {/* Background Decorative Blurs & Texture */}
      <div className="absolute top-[-10%] left-[-10%] w-[45%] h-[45%] bg-purple-900/15 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[45%] h-[45%] bg-indigo-950/20 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'radial-gradient(#fff 1px, transparent 0)', backgroundSize: '40px 40px' }}></div>

      <div className="max-w-6xl mx-auto relative z-10">
        
        {/* Header Section */}
        <header className="bg-[#0f0f15]/80 backdrop-blur-xl border border-white/10 shadow-2xl rounded-3xl p-8 mb-10 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-500/10 rounded-2xl border border-purple-500/20 shadow-[0_0_15px_rgba(168,85,247,0.15)]">
              <ShieldCheck className="text-purple-400 w-8 h-8" />
            </div>
            <div>
              <h1 className="text-3xl font-black tracking-tight text-white uppercase italic">
                Proctored <span className="text-purple-500">Assessment</span>
              </h1>
              <div className="flex items-center gap-2 text-slate-400 text-sm font-medium mt-1">
                <Cpu size={14} className="text-purple-400/80" />
                <span>AI Integrity Engine v3.1</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3 bg-black/40 px-4 py-2 rounded-full border border-white/5">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.8)]" />
            <span className="text-xs font-bold text-red-400 tracking-widest uppercase">Monitoring Active</span>
          </div>
        </header>

        {/* Rules Alert */}
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-2xl p-5 mb-10 flex items-start gap-4">
          <AlertTriangle className="text-amber-500 shrink-0 mt-0.5" size={20} />
          <p className="text-amber-200/80 text-sm leading-relaxed">
            <span className="font-bold text-amber-500 uppercase tracking-tighter mr-2">Security Protocol:</span> 
            Leaving this window, right-clicking, or attempting to paste external code will be logged as a violation. All keyboard activity is recorded and synchronized in real-time.
          </p>
        </div>

        {/* Questions Loop */}
        <div className="space-y-12">
          {questions.map((q, index) => (
            <div key={q.id} className="bg-[#0f0f15]/80 backdrop-blur-xl border border-white/10 shadow-2xl rounded-3xl overflow-hidden transition-all duration-300 hover:border-purple-500/20">
              
              {/* Card Header Area */}
              <div className="p-8 border-b border-white/5 bg-white/[0.02] flex justify-between items-center">
                <div className="flex items-center gap-4">
                  <span className="text-4xl font-black text-white/5 italic select-none">0{index + 1}</span>
                  <h3 className="text-xl font-bold text-purple-100 tracking-tight">{q.function_name}</h3>
                </div>
                <span className="px-4 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-[10px] font-black uppercase tracking-[0.2em]">
                  {q.difficulty || 'MEDIUM'}
                </span>
              </div>

              <div className="p-8 space-y-8">
                {/* Fixed Question Display: Expandable and Wrapped */}
                <div className="bg-white/[0.02] p-6 rounded-2xl border border-white/[0.05] shadow-inner">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-1 h-4 bg-purple-500 rounded-full" />
                    <span className="text-[10px] font-black text-purple-400 uppercase tracking-widest">Description</span>
                  </div>
                  <div className="text-slate-300 text-base leading-relaxed whitespace-pre-wrap break-words">
                    {q.question_text}
                  </div>
                </div>

                {/* Monaco Editor Container */}
                <div className="rounded-2xl overflow-hidden border border-white/10 shadow-[0_20px_50px_rgba(0,0,0,0.5)]">
                  <Editor
                    height="450px"
                    defaultLanguage="python"
                    theme="custom-dark"
                    defaultValue={`def ${q.function_name}():\n    # Implement your solution below\n    pass`}
                    beforeMount={(monaco) => {
                      monaco.editor.defineTheme('custom-dark', {
                        base: 'vs-dark',
                        inherit: true,
                        rules: [],
                        colors: {
                          'editor.background': '#0c0c12',
                          'editor.lineHighlightBackground': '#14121e',
                          'editorCursor.foreground': '#a855f7',
                          'editor.selectionBackground': '#a855f733',
                          'editorLineNumber.foreground': '#4b5563',
                        },
                      });
                    }}
                    options={{
                      minimap: { enabled: false },
                      fontSize: 14,
                      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                      lineNumbersMinChars: 3,
                      scrollBeyondLastLine: false,
                      padding: { top: 20, bottom: 20 },
                      contextmenu: false,
                      smoothScrolling: true,
                      cursorSmoothCaretAnimation: "on",
                    }}
                    onMount={(editor) => {
                      // Block Paste Command (Ctrl/Cmd + V)
                      editor.onKeyDown((e) => {
                        const { keyCode, ctrlKey, metaKey } = e;
                        if ((ctrlKey || metaKey) && keyCode === 82) {
                          e.preventDefault();
                          e.stopPropagation();
                          reportViolation("Keyboard Paste Attempted");
                          alert("🚨 Security Alert: Paste functionality is disabled.");
                        }
                        
                        // Pass to hook for logging
                        handleKeyDown({
                          key: e.browserEvent.key,
                          timestamp: Date.now()
                        } as any);
                      });
                    }}
                    onChange={(val) => setSolutions({...solutions, [q.id]: val || ''})}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer Submit Button */}
        <footer className="mt-16 mb-20 text-center">
          <button 
            onClick={handleSubmit}
            disabled={submitting || questions.length === 0}
            className="group relative px-16 py-6 bg-purple-600 hover:bg-purple-500 text-white rounded-3xl font-black text-xl transition-all duration-300 shadow-[0_10px_40px_-10px_rgba(139,92,246,0.6)] hover:scale-[1.03] active:scale-95 disabled:bg-slate-800 disabled:text-slate-500 disabled:shadow-none disabled:cursor-not-allowed"
          >
            <div className="flex items-center gap-4">
              {submitting ? (
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-white"></div>
              ) : (
                <Lock size={22} className="group-hover:rotate-12 transition-transform" />
              )}
              <span className="tracking-widest uppercase">{submitting ? "ENCRYPTING DATA..." : "FINALIZE & SUBMIT"}</span>
            </div>
          </button>
          <p className="text-slate-500 mt-8 text-sm font-medium italic opacity-60">
            This session is being verified against our cheating-detection database.
          </p>
        </footer>

      </div>
    </div>
  );
};

export default AssessmentPage;