import { useEffect, useRef, useCallback } from 'react';

interface SecurityLog {
  type: string;
  details: string;
  timestamp: string;
}

interface Keystroke {
  key: string;
  timestamp: number;
}

export const useSecurityShield = (token: string) => {
  const keystrokeBuffer = useRef<Keystroke[]>([]);
  // Use a ref to track if we are currently sending to avoid duplicate requests
  const isReporting = useRef(false);

  // 1. Function to log major violations (Tab switch, Paste)
  const reportViolation = useCallback(async (log: SecurityLog) => {
    if (!token || token === 'unknown') return;
    
    try {
      await fetch('${import.meta.env.VITE_BACKEND_URL}/services/log-violation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: token,
          violation_type: log.type,
          details: log.details,
        }),
      });
    } catch (error) {
      console.error("Security Shield Error:", error);
    }
  }, [token]);

  // 2. Setup Event Listeners for Environment Monitoring
  useEffect(() => {
    if (!token) return;

    const handleBlur = () => {
      reportViolation({
        type: 'tab_switch',
        details: 'Candidate left the assessment window',
        timestamp: new Date().toISOString(),
      });
    };

    const handlePaste = (e: ClipboardEvent) => {
      e.preventDefault();
      reportViolation({
        type: 'paste_attempt',
        details: 'Blocked attempt to paste code into editor',
        timestamp: new Date().toISOString(),
      });
    };

    const handleCopy = (e: ClipboardEvent) => {
      // Prevents copying the question text to send to a phone AI
      e.preventDefault();
      reportViolation({
        type: 'copy_attempt',
        details: 'Blocked attempt to copy test content',
        timestamp: new Date().toISOString(),
      });
    };

    const handleContextMenu = (e: MouseEvent) => e.preventDefault();

    window.addEventListener('blur', handleBlur);
    window.addEventListener('paste', handlePaste);
    window.addEventListener('copy', handleCopy);
    window.addEventListener('contextmenu', handleContextMenu);

    return () => {
      window.removeEventListener('blur', handleBlur);
      window.removeEventListener('paste', handlePaste);
      window.removeEventListener('copy', handleCopy);
      window.removeEventListener('contextmenu', handleContextMenu);
    };
  }, [token, reportViolation]);

  // 3. Function to analyze typing patterns (The "Phone AI" Detector)
  const handleKeyDown = useCallback(async (e: { key: string; timestamp: number }) => {
    keystrokeBuffer.current.push({ key: e.key, timestamp: e.timestamp });

    // Send telemetry data in chunks of 20 keystrokes
    if (keystrokeBuffer.current.length >= 20) {
      const payload = {
        token: token,
        events: [...keystrokeBuffer.current]
      };

      try {
        await fetch('${import.meta.env.VITE_BACKEND_URL}/services/telemetry', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } catch (err) {
        console.error("Telemetry Sync Failed");
      }

      keystrokeBuffer.current = [];
    }
  }, [token]);

  return { handleKeyDown };
};