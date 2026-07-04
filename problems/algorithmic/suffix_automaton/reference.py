#!/usr/bin/env python3
"""Suffix Automaton — Count Distinct Substrings.
Build a suffix automaton for 'banana' and count distinct substrings.
"""
import sys

class SAMState:
    __slots__ = ['length', 'link', 'next']
    def __init__(self):
        self.length = 0
        self.link = -1
        self.next = {}

class SuffixAutomaton:
    def __init__(self, s):
        self.states = [SAMState()]
        self.last = 0
        for ch in s:
            self._extend(ch)
    
    def _extend(self, c):
        p = self.last
        cur = len(self.states)
        self.states.append(SAMState())
        self.states[cur].length = self.states[p].length + 1
        while p != -1 and c not in self.states[p].next:
            self.states[p].next[c] = cur
            p = self.states[p].link
        if p == -1:
            self.states[cur].link = 0
        else:
            q = self.states[p].next[c]
            if self.states[p].length + 1 == self.states[q].length:
                self.states[cur].link = q
            else:
                clone = len(self.states)
                self.states.append(SAMState())
                self.states[clone].length = self.states[p].length + 1
                self.states[clone].next = self.states[q].next.copy()
                self.states[clone].link = self.states[q].link
                while p != -1 and self.states[p].next.get(c) == q:
                    self.states[p].next[c] = clone
                    p = self.states[p].link
                self.states[q].link = clone
                self.states[cur].link = clone
        self.last = cur
    
    def count_distinct_substrings(self):
        return sum(s.length - self.states[s.link].length for s in self.states[1:])

def main():
    s = "banana"
    sam = SuffixAutomaton(s)
    count = sam.count_distinct_substrings()
    print(f"String: {s}")
    print(f"Distinct substrings: {count}")

if __name__ == "__main__":
    main()
