"""
DSA Visualizer - Problem Library
Curated DSA problems for visualization.
"""
from app.models.events import DSAProblem

PROBLEMS: dict[str, DSAProblem] = {
    "two_sum": DSAProblem(
        id="two_sum",
        title="Two Sum",
        description="Find two numbers in an array that add up to a target.",
        difficulty="Easy",
        tags=["array", "hash-map", "two-pointers"],
        initial_vars={"nums": [2, 7, 11, 15], "target": 9},
        code='''\
nums = [2, 7, 11, 15]
target = 9
seen = {}

for i in range(len(nums)):
    need = target - nums[i]
    if need in seen:
        result = [seen[need], i]
    else:
        seen[nums[i]] = i
'''
    ),
    "binary_search": DSAProblem(
        id="binary_search",
        title="Binary Search",
        description="Search a sorted array using divide-and-conquer.",
        difficulty="Easy",
        tags=["array", "binary-search", "divide-and-conquer"],
        initial_vars={"nums": [1, 3, 5, 7, 9, 11, 13], "target": 7},
        code='''\
nums = [1, 3, 5, 7, 9, 11, 13]
target = 7
left = 0
right = len(nums) - 1
result = -1

while left <= right:
    mid = (left + right) // 2
    if nums[mid] == target:
        result = mid
        left = right + 1
    elif nums[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
'''
    ),
    "bubble_sort": DSAProblem(
        id="bubble_sort",
        title="Bubble Sort",
        description="Sort an array by repeatedly swapping adjacent elements.",
        difficulty="Easy",
        tags=["array", "sorting"],
        initial_vars={"arr": [64, 34, 25, 12, 22, 11, 90]},
        code='''\
arr = [64, 34, 25, 12, 22, 11, 90]
n = len(arr)

for i in range(n):
    for j in range(0, n - i - 1):
        if arr[j] > arr[j + 1]:
            temp = arr[j]
            arr[j] = arr[j + 1]
            arr[j + 1] = temp
'''
    ),
    "fibonacci": DSAProblem(
        id="fibonacci",
        title="Fibonacci Sequence",
        description="Compute the nth Fibonacci number iteratively.",
        difficulty="Easy",
        tags=["dynamic-programming", "iteration"],
        initial_vars={"n": 8},
        code='''\
n = 8
a = 0
b = 1
result = 0

for i in range(n):
    result = a + b
    a = b
    b = result
'''
    ),
    "max_subarray": DSAProblem(
        id="max_subarray",
        title="Maximum Subarray (Kadane's)",
        description="Find the contiguous subarray with the largest sum.",
        difficulty="Medium",
        tags=["array", "dynamic-programming", "greedy"],
        initial_vars={"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]},
        code='''\
nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
max_sum = nums[0]
current = nums[0]

for i in range(1, len(nums)):
    current = max(nums[i], current + nums[i])
    if current > max_sum:
        max_sum = current
'''
    ),
    "palindrome_check": DSAProblem(
        id="palindrome_check",
        title="Palindrome Check",
        description="Check if a string reads the same forwards and backwards.",
        difficulty="Easy",
        tags=["string", "two-pointers"],
        initial_vars={"s": "racecar"},
        code='''\
s = "racecar"
left = 0
right = len(s) - 1
is_palindrome = True

while left < right:
    if s[left] != s[right]:
        is_palindrome = False
        left = right
    else:
        left = left + 1
        right = right - 1
'''
    ),
    "stack_operations": DSAProblem(
        id="stack_operations",
        title="Stack Operations",
        description="Demonstrate LIFO stack operations using a Python list.",
        difficulty="Easy",
        tags=["stack", "data-structure"],
        initial_vars={},
        code='''\
stack = []
stack.append(1)
stack.append(2)
stack.append(3)
top = stack[-1]
popped = stack.pop()
size = len(stack)
is_empty = len(stack) == 0
'''
    ),
    "count_occurrences": DSAProblem(
        id="count_occurrences",
        title="Count Occurrences",
        description="Count how many times each element appears using a hash map.",
        difficulty="Easy",
        tags=["array", "hash-map"],
        initial_vars={"nums": [1, 2, 3, 2, 1, 2, 4]},
        code='''\
nums = [1, 2, 3, 2, 1, 2, 4]
counts = {}

for num in nums:
    if num in counts:
        counts[num] = counts[num] + 1
    else:
        counts[num] = 1

most_common = 0
for num in counts:
    if counts[num] > most_common:
        most_common = counts[num]
'''
    ),
}


def get_problem(problem_id: str) -> DSAProblem | None:
    return PROBLEMS.get(problem_id)


def list_problems() -> list[dict]:
    return [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "difficulty": p.difficulty,
            "tags": p.tags,
        }
        for p in PROBLEMS.values()
    ]
