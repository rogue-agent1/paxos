#!/usr/bin/env python3
"""Paxos consensus — single-decree Paxos for distributed agreement.

One file. Zero deps. Does one thing well.

Implements the classic Paxos algorithm (Lamport 1998) with proposers,
acceptors, and learners. Guarantees safety (agreement) even with failures.
"""
import random, sys
from collections import Counter

class Proposal:
    __slots__ = ('number', 'value')
    def __init__(self, number, value=None):
        self.number = number
        self.value = value
    def __repr__(self):
        return f"P({self.number}, {self.value})"

class Acceptor:
    def __init__(self, name, fail_rate=0.0):
        self.name = name
        self.fail_rate = fail_rate
        self.promised = -1       # highest proposal number promised
        self.accepted_num = -1   # highest accepted proposal number
        self.accepted_val = None # accepted value

    def prepare(self, proposal_num):
        """Phase 1b: respond to prepare request."""
        if random.random() < self.fail_rate:
            return None  # Simulated failure
        if proposal_num > self.promised:
            self.promised = proposal_num
            return ("promise", self.accepted_num, self.accepted_val)
        return ("reject", self.promised, None)

    def accept(self, proposal_num, value):
        """Phase 2b: respond to accept request."""
        if random.random() < self.fail_rate:
            return None
        if proposal_num >= self.promised:
            self.promised = proposal_num
            self.accepted_num = proposal_num
            self.accepted_val = value
            return ("accepted", proposal_num, value)
        return ("reject", self.promised, None)

class Proposer:
    def __init__(self, name, acceptors, proposal_start=0):
        self.name = name
        self.acceptors = acceptors
        self.proposal_num = proposal_start
        self.quorum = len(acceptors) // 2 + 1

    def propose(self, value):
        """Run full Paxos protocol to get value chosen."""
        self.proposal_num += 1
        n = self.proposal_num

        # Phase 1a: Send prepare
        promises = []
        for a in self.acceptors:
            resp = a.prepare(n)
            if resp and resp[0] == "promise":
                promises.append(resp)

        if len(promises) < self.quorum:
            return None  # Failed to get quorum

        # Phase 1b: Check if any acceptor already accepted a value
        highest_accepted = -1
        chosen_value = value
        for _, acc_num, acc_val in promises:
            if acc_num > highest_accepted and acc_val is not None:
                highest_accepted = acc_num
                chosen_value = acc_val  # Must use previously accepted value

        # Phase 2a: Send accept
        accepted = []
        for a in self.acceptors:
            resp = a.accept(n, chosen_value)
            if resp and resp[0] == "accepted":
                accepted.append(resp)

        if len(accepted) >= self.quorum:
            return chosen_value  # Value chosen!
        return None

def run_paxos(n_acceptors=5, fail_rate=0.0):
    acceptors = [Acceptor(f"A{i}", fail_rate) for i in range(n_acceptors)]
    p1 = Proposer("P1", acceptors, proposal_start=0)
    p2 = Proposer("P2", acceptors, proposal_start=100)

    result1 = p1.propose("value-A")
    result2 = p2.propose("value-B")
    return result1, result2, acceptors

def main():
    random.seed(42)
    print("=== Single-Decree Paxos ===\n")

    # Basic consensus
    r1, r2, acceptors = run_paxos(5, fail_rate=0.0)
    print(f"Proposer 1 chose: {r1}")
    print(f"Proposer 2 chose: {r2}")
    vals = {a.accepted_val for a in acceptors if a.accepted_val}
    print(f"Accepted values: {vals}")
    if len(vals) <= 1:
        print("✓ Agreement achieved")

    # With failures
    print("\n=== With 20% failure rate ===")
    successes = 0
    agreements = 0
    for trial in range(100):
        random.seed(trial)
        r1, r2, acceptors = run_paxos(5, fail_rate=0.2)
        if r1 or r2:
            successes += 1
        vals = {a.accepted_val for a in acceptors if a.accepted_val}
        if len(vals) <= 1:
            agreements += 1
    print(f"Trials: 100")
    print(f"At least one proposer succeeded: {successes}")
    print(f"Safety (agreement) maintained: {agreements}/100")

    # Competing proposers
    print("\n=== 5 Competing Proposers ===")
    random.seed(99)
    acceptors = [Acceptor(f"A{i}") for i in range(7)]
    proposers = [Proposer(f"P{i}", acceptors, i * 100) for i in range(5)]
    results = {}
    for p in proposers:
        r = p.propose(f"val-{p.name}")
        results[p.name] = r
    print(f"Results: {results}")
    vals = {a.accepted_val for a in acceptors if a.accepted_val}
    print(f"Final accepted: {vals}")

if __name__ == "__main__":
    main()
