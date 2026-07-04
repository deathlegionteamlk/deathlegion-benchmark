#!/usr/bin/env python3
"""2D Fenwick Tree — Range Sum Queries.
Support point add and prefix sum queries on a 2D grid.
"""
import sys

class Fenwick2D:
    def __init__(self, n, m):
        self.n = n
        self.m = m
        self.bit = [[0] * (m + 1) for _ in range(n + 1)]
    
    def add(self, x, y, delta):
        i = x
        while i <= self.n:
            j = y
            while j <= self.m:
                self.bit[i][j] += delta
                j += j & -j
            i += i & -i
    
    def sum(self, x, y):
        res = 0
        i = x
        while i > 0:
            j = y
            while j > 0:
                res += self.bit[i][j]
                j -= j & -j
            i -= i & -i
        return res
    
    def range_sum(self, x1, y1, x2, y2):
        return (self.sum(x2, y2) - self.sum(x1 - 1, y2)
                - self.sum(x2, y1 - 1) + self.sum(x1 - 1, y1 - 1))

def main():
    bit = Fenwick2D(5, 5)
    updates = [(1, 1, 3), (2, 3, 5), (3, 2, 7), (4, 4, 2), (5, 5, 8),
               (1, 5, 4), (5, 1, 6)]
    for x, y, val in updates:
        bit.add(x, y, val)
    
    queries = [
        (1, 1, 5, 5),
        (2, 2, 4, 4),
        (3, 3, 5, 5)
    ]
    results = [bit.range_sum(x1, y1, x2, y2) for (x1, y1, x2, y2) in queries]
    print(f"Final sums: {results}")

if __name__ == "__main__":
    main()
