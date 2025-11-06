BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 9000

# Example problems. Optionally align with backend replicated keys.
PROBLEMS = {
    "two-sum": {
        "title": "Two Sum",
        "prompt": "Given nums and target, return indices of two numbers that add to target.",
        "starter_code": """
def two_sum(nums, target):
    # TODO: implement
    return [-1, -1]
""".strip(),
        "tests": """
assert two_sum([2,7,11,15], 9) == [0,1]
assert two_sum([3,2,4], 6) == [1,2]
""".strip(),
    },
    "fizzbuzz": {
        "title": "FizzBuzz",
        "prompt": "Print numbers 1..n, replacing multiples of 3 with Fizz, 5 with Buzz.",
        "starter_code": """
def fizzbuzz(n):
    for i in range(1, n+1):
        print(i)
""".strip(),
        "tests": """
# Basic smoke test
fizzbuzz(15)
""".strip(),
    },
}




