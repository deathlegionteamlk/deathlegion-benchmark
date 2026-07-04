#!/usr/bin/env python3
"""Brute force approach with an intentional bug: incorrect line evaluation.
Wrongly computes m*x + b as m*x - b, producing wrong results.
"""
import sys

def evaluate_lines_wrong(lines, x):
    # BUG: subtracts b instead of adding b
    return max(m * x - b for m, b in lines)

def main():
    xs = [-5, -3, 0, 2, 7]
    lines = [(3, 5), (-1, 10), (2, -4), (-2, 6), (0, 30)]
    results = [evaluate_lines_wrong(lines, x) for x in xs]
    print(f"Query results: {results}")

if __name__ == "__main__":
    main()
