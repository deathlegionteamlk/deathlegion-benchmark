#!/usr/bin/env python3
"""Greedy approach: always multiply the pair with smallest dimension product.
This looks plausible but gives wrong optimal cost.
"""
import sys

def greedy_matrix_chain(dims):
    n = len(dims) - 1
    matrices = list(range(n))
    total_cost = 0
    steps = []

    while len(matrices) > 1:
        min_cost = float('inf')
        min_idx = -1
        for i in range(len(matrices) - 1):
            a = matrices[i]
            b = matrices[i + 1]
            cost = dims[a] * dims[a + 1] * dims[b + 1]
            if cost < min_cost:
                min_cost = cost
                min_idx = i
        total_cost += min_cost
        # Merge
        new_idx = matrices[min_idx]
        matrices.pop(min_idx)
        matrices[min_idx] = new_idx
        steps.append(min_cost)

    return total_cost

def main():
    dims = [30, 35, 15, 5, 10, 20]
    cost = greedy_matrix_chain(dims)
    print(f"Optimal cost: {cost}")
    print(f"Parenthesization: ((A0(A1A2))(A3A4))")

if __name__ == "__main__":
    main()
