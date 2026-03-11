#!/usr/bin/env python3
"""Paxos — single-decree consensus protocol simulation."""
import sys, random

class Proposer:
    def __init__(self, id):
        self.id = id; self.n = 0
    def prepare(self):
        self.n += 1
        return (self.n, self.id)

class Acceptor:
    def __init__(self, id):
        self.id = id; self.promised = None
        self.accepted_n = None; self.accepted_val = None
    def on_prepare(self, n):
        if self.promised is None or n > self.promised:
            self.promised = n
            return {"ok": True, "accepted_n": self.accepted_n, "accepted_val": self.accepted_val}
        return {"ok": False}
    def on_accept(self, n, value):
        if self.promised is None or n >= self.promised:
            self.promised = n; self.accepted_n = n; self.accepted_val = value
            return True
        return False

def run_paxos(n_acceptors=5, proposals=None):
    if not proposals:
        proposals = ["alpha", "beta"]
    acceptors = [Acceptor(i) for i in range(n_acceptors)]
    quorum = n_acceptors // 2 + 1
    decided = None

    for idx, value in enumerate(proposals):
        p = Proposer(idx)
        n = p.prepare()
        print(f"\nProposer {idx} proposes '{value}' with n={n}")

        # Phase 1: Prepare
        promises = []
        for a in acceptors:
            if random.random() > 0.05:  # 5% message loss
                resp = a.on_prepare(n)
                if resp["ok"]:
                    promises.append(resp)
                    print(f"  Acceptor {a.id}: PROMISE")
                else:
                    print(f"  Acceptor {a.id}: REJECT (promised higher)")

        if len(promises) < quorum:
            print(f"  ❌ No quorum ({len(promises)}/{quorum})")
            continue

        # Phase 2: Accept (use previously accepted value if any)
        prior = [p for p in promises if p["accepted_n"] is not None]
        use_val = max(prior, key=lambda x: x["accepted_n"])["accepted_val"] if prior else value
        print(f"  Quorum reached! Sending ACCEPT with value='{use_val}'")

        accepted = 0
        for a in acceptors:
            if a.on_accept(n, use_val):
                accepted += 1

        if accepted >= quorum:
            decided = use_val
            print(f"  ✅ CONSENSUS: '{use_val}'")
        else:
            print(f"  ❌ Accept failed ({accepted}/{quorum})")

    return decided

if __name__ == "__main__":
    random.seed(42)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    print(f"Paxos simulation: {n} acceptors, 2 competing proposers")
    result = run_paxos(n, ["alpha", "beta"])
    print(f"\nFinal decided value: {result}")
