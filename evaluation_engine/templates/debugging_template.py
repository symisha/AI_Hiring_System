TEMPLATE_NAME = "bug_fix_even_average"


def reference_solution(nums):
    even_numbers = [n for n in nums if n % 2 == 0]
    if len(even_numbers) == 0:
        return 0
    return sum(even_numbers) / len(even_numbers)


def generate_test_cases():
    return [
        {"input": [2, 4, 6], "expected": 4.0},
        {"input": [1, 3, 5], "expected": 0},
        {"input": [10, 15, 20], "expected": 15.0},
        {"input": [], "expected": 0},
    ]