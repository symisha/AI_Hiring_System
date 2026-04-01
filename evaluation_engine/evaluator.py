import traceback

class Evaluator:

    def __init__(self, template_module):
        self.template = template_module

    def evaluate_function(self, candidate_function):
        test_cases = self.template.generate_test_cases()
        passed = 0
        total = len(test_cases)

        for case in test_cases:
            try:
                if isinstance(case["input"], tuple):
                    result = candidate_function(*case["input"])
                else:
                    result = candidate_function(case["input"])

                if result == case["expected"]:
                    passed += 1

            except Exception:
                print("Error in candidate code:")
                print(traceback.format_exc())

        score = (passed / total) * 100

        return {
            "passed": passed,
            "total": total,
            "score": score
        }