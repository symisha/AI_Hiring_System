import random
from typing import List

TEMPLATE_NAME = "sliding_window_max_sum"

def generate_input():
    arr = [random.randint(-20, 50) for _ in range(10)]
    k = random.randint(1, 5)
    return arr, k


def reference_solution(arr: List[int], k: int) -> int:
    max_sum = float('-inf')
    for i in range(len(arr) - k + 1):
        window_sum = sum(arr[i:i+k])
        max_sum = max(max_sum, window_sum)
    return max_sum


def generate_test_cases(n=5):
    test_cases = []
    for _ in range(n):
        arr, k = generate_input()
        expected = reference_solution(arr, k)
        test_cases.append({
            "input": (arr, k),
            "expected": expected
        })
    return test_cases