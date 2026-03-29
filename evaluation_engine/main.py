from evaluator import Evaluator
import templates.sliding_window as sliding_window
import templates.debugging_template as debugging


# Simulated Candidate Code (DSA)
def candidate_sliding_window(arr, k):
    # intentionally correct
    max_sum = float('-inf')
    for i in range(len(arr) - k + 1):
        max_sum = max(max_sum, sum(arr[i:i+k]))
    return max_sum


# Simulated Candidate Code (Debugging)
def candidate_debug(nums):
    even_numbers = [n for n in nums if n % 2 == 0]
    if len(even_numbers) == 0:
        return 0
    return sum(even_numbers) / len(even_numbers)


if __name__ == "__main__":

    print("Evaluating Sliding Window Template")
    evaluator1 = Evaluator(sliding_window)
    result1 = evaluator1.evaluate_function(candidate_sliding_window)
    print(result1)

    print("\nEvaluating Debugging Template")
    evaluator2 = Evaluator(debugging)
    result2 = evaluator2.evaluate_function(candidate_debug)
    print(result2)