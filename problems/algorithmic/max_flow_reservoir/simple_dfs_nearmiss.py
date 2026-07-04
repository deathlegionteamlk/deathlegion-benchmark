#!/usr/bin/env python3
"""Simple DFS path-finding approach. Finds any path from source to sink
but doesn't properly handle residual edges or capacity management.
"""
import sys

def simple_max_flow(edges, n, s, t):
    adj = [[] for _ in range(n)]
    for u, v, cap in edges:
        adj[u].append([v, cap])
    
    def dfs(u, t, visited, flow):
        if u == t:
            return flow
        visited[u] = True
        for i, (v, cap) in enumerate(adj[u]):
            if not visited[v] and cap > 0:
                ret = dfs(v, t, visited, min(flow, cap))
                if ret > 0:
                    adj[u][i][1] -= ret
                    return ret
        return 0
    
    total = 0
    while True:
        visited = [False] * n
        pushed = dfs(s, t, visited, 10**9)
        if pushed == 0:
            break
        total += pushed
    return total

def main():
    edges = [
        (0, 1, 16), (0, 2, 13), (1, 2, 10),
        (1, 3, 12), (2, 1, 4), (2, 4, 14),
        (3, 2, 9), (3, 5, 20), (4, 3, 7), (4, 5, 4)
    ]
    flow = simple_max_flow(edges, 6, 0, 5)
    # This simple DFS doesn't add reverse edges, so it returns a suboptimal flow
    print(f"Max flow: {flow}")

if __name__ == "__main__":
    main()
