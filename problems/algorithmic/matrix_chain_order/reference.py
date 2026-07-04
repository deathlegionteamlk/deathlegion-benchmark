#!/usr/bin/env python3
"""Matrix Chain Multiplication — Optimal Parenthesization.
Given dimensions [30, 35, 15, 5, 10, 20], compute minimum scalar multiplications.
"""
import sys

def matrix_chain_order(dims):
    n = len(dims) - 1
    dp = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    split[i][j] = k
    return dp[0][n - 1], split

def build_parenthesization(split, i, j):
    if i == j:
        return f"A{i}"
    k = split[i][j]
    left = build_parenthesization(split, i, k)
    right = build_parenthesization(split, k + 1, j)
    return f"({left}{right})"

def main():
    dims = [30, 35, 15, 5, 10, 20]
    cost, split = matrix_chain_order(dims)
    paren = build_parenthesization(split, 0, len(dims) - 2)
    print(f"Optimal cost: {cost}")
    print(f"Parenthesization: {paren}")

if __name__ == "__main__":
    main()
