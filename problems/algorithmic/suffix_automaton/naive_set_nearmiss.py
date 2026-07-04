#!/usr/bin/env python3
"""Naive set-based approach: enumerate all substrings.
This uses O(n^2) memory even for small strings and double-counts when
the set-based dedup misses substring boundaries.
"""
import sys

def count_distinct_naive(s):
    seen = set()
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            seen.add(s[i:j])
    return len(seen)

def main():
    s = "banana"
    count = count_distinct_naive(s)
    # Bug: prints the wrong string in output — says "String: banana" correctly
    # but the count is actually correct here (15) so this near-miss passes.
    # Let me make it actually wrong:
    # The issue: we are counting substrings correctly but let's make a logic error.
    count = count_distinct_naive(s)
    print(f"String: {s}")
    print(f"Distinct substrings: {count - 1}")  # Off-by-one error

if __name__ == "__main__":
    main()
