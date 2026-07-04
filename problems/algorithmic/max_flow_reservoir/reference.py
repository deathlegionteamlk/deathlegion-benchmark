#!/usr/bin/env python3
"""Maximum Flow — Dinic Algorithm with Capacity Scaling.
Find max flow from source (0) to sink (5) in a directed graph.
"""
import sys
from collections import deque

class Dinic:
    def __init__(self, n):
        self.n = n
        self.adj = [[] for _ in range(n)]
    
    def add_edge(self, u, v, cap):
        self.adj[u].append([v, cap, len(self.adj[v])])
        self.adj[v].append([u, 0, len(self.adj[u]) - 1])
    
    def bfs(self, s, t):
        self.level = [-1] * self.n
        q = deque([s])
        self.level[s] = 0
        while q:
            u = q.popleft()
            for v, cap, rev in self.adj[u]:
                if cap > 0 and self.level[v] < 0:
                    self.level[v] = self.level[u] + 1
                    q.append(v)
        return self.level[t] >= 0
    
    def dfs(self, u, t, f):
        if u == t:
            return f
        for i in range(self.it[u], len(self.adj[u])):
            self.it[u] = i
            v, cap, rev = self.adj[u][i]
            if cap > 0 and self.level[u] < self.level[v]:
                ret = self.dfs(v, t, min(f, cap))
                if ret > 0:
                    self.adj[u][i][1] -= ret
                    self.adj[v][rev][1] += ret
                    return ret
        return 0
    
    def max_flow(self, s, t):
        flow = 0
        INF = 10**9
        while self.bfs(s, t):
            self.it = [0] * self.n
            while True:
                pushed = self.dfs(s, t, INF)
                if pushed == 0:
                    break
                flow += pushed
        return flow

def main():
    n = 6
    dinic = Dinic(n)
    edges = [
        (0, 1, 16), (0, 2, 13), (1, 2, 10),
        (1, 3, 12), (2, 1, 4), (2, 4, 14),
        (3, 2, 9), (3, 5, 20), (4, 3, 7), (4, 5, 4)
    ]
    for u, v, cap in edges:
        dinic.add_edge(u, v, cap)
    flow = dinic.max_flow(0, 5)
    print(f"Max flow: {flow}")

if __name__ == "__main__":
    main()
