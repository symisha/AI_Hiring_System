import requests
import base64
import time

class Judge0PublicService:
    def __init__(self):
        self.base_url = "https://ce.judge0.com"

    def run_automated_test(self, candidate_code, question_meta):
        # 1. REMOVE the '*' so the list is passed as a single argument
        # 2. Use repr() for the test_input to ensure strings/lists are formatted correctly for Python
        driver = f"\n\nprint({question_meta['function_name']}({repr(question_meta['test_input'])}))"
        
        full_code = candidate_code.strip() + driver

        payload = {
            "source_code": base64.b64encode(full_code.encode()).decode(),
            "language_id": 71, # Python 3
            # IMPORTANT: Let Judge0 handle the base64 encoding for stdout comparison
            "expected_output": base64.b64encode(str(question_meta['expected_output']).encode()).decode()
        }
        
        # Use ?base64_encoded=true so Judge0 returns everything in base64
        response = requests.post(f"{self.base_url}/submissions?wait=false&base64_encoded=true", json=payload)
        token = response.json().get("token")
        
        return self.poll_for_result(token, question_meta['expected_output'])

    def poll_for_result(self, token, expected):
        for _ in range(10):
            res = requests.get(f"{self.base_url}/submissions/{token}")
            data = res.json()
            
            if data.get("status", {}).get("id") > 2:
                def safe_get(key):
                    val = data.get(key)
                    if not val: return ""
                    try:
                        return base64.b64decode(val).decode('utf-8', errors='replace').strip()
                    except: return ""

                actual_raw = safe_get("stdout")
                actual_clean = actual_raw.replace(" ", "")
                expected_clean = str(expected).strip().replace(" ", "")
                error_details = safe_get("stderr") or safe_get("compile_output")
                
                return {
                    "success": actual_clean == expected_clean,
                    "actual": actual_raw,
                    "status": data.get("status", {}).get("description"),
                    "error_details": error_details
                }
            time.sleep(1)
        return {"error": "Timed out"}