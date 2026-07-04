#!/usr/bin/env python3
"""Li Chao Segment Tree for Maximum Line Queries.
Insert lines (m, b) and query max y = m*x + b at given x points.
"""
import sys

class LiChaoTree:
    def __init__(self, xs):
        self.xs = sorted(xs)
        self.n = len(self.xs)
        size = 1
        while size < self.n:
            size <<= 1
        self.size = size
        self.tree = [(0, float('-inf'))] * (2 * size)
    
    def _f(self, line, x):
        m, b = line
        return m * x + b
    
    def add_line(self, line):
        self._add_line(line, 0, 0, self.size)
    
    def _add_line(self, line, node, l, r):
        m = (l + r) // 2
        left_x = self.xs[l] if l < self.n else self.xs[-1]
        mid_x = self.xs[m] if m < self.n else self.xs[-1]
        cur = self.tree[node]
        if self._f(cur, left_x) <= self._f(line, left_x):
            self.tree[node], line = line, cur
        if r - l == 1:
            return
        if self._f(self.tree[node], mid_x) < self._f(line, mid_x):
            self.tree[node], line = line, self.tree[node]
            self._add_line(line, 2 * node + 1, m, r)
        else:
            self._add_line(line, 2 * node + 2, l, m)
    
    def query(self, x):
        idx = self.xs.index(x)
        node = 0
        l, r = 0, self.size
        best = float('-inf')
        while True:
            best = max(best, self._f(self.tree[node], x))
            if r - l == 1:
                break
            m = (l + r) // 2
            if idx < m:
                node = 2 * node + 2
                r = m
            else:
                node = 2 * node + 1
                l = m
        return best

def main():
    xs = [-5, -3, 0, 2, 7]
    lichao = LiChaoTree(xs)
    lines = [(3, 5), (-1, 10), (2, -4), (-2, 6), (0, 30)]
    for line in lines:
        lichao.add_line(line)
    results = [lichao.query(x) for x in xs]
    print(f"Query results: {results}")

if __name__ == "__main__":
    main()
