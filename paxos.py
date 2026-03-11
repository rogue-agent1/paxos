#!/usr/bin/env python3
"""Paxos consensus simulation (single-decree)."""
import sys, random
random.seed(42)
class Acceptor:
    def __init__(self,id): self.id=id; self.promised=0; self.accepted_n=0; self.accepted_v=None
    def prepare(self,n):
        if n>self.promised: self.promised=n; return True,self.accepted_n,self.accepted_v
        return False,0,None
    def accept(self,n,v):
        if n>=self.promised: self.promised=n; self.accepted_n=n; self.accepted_v=v; return True
        return False
class Proposer:
    def __init__(self,id,value): self.id=id; self.value=value; self.n=id
    def propose(self,acceptors,quorum):
        self.n+=10
        # Phase 1: Prepare
        promises=[]; 
        for a in acceptors:
            ok,an,av=a.prepare(self.n)
            if ok: promises.append((an,av))
        if len(promises)<quorum: return None
        # Use highest accepted value if any
        highest=max(promises,key=lambda x:x[0])
        if highest[1] is not None: self.value=highest[1]
        # Phase 2: Accept
        accepts=sum(1 for a in acceptors if a.accept(self.n,self.value))
        if accepts>=quorum: return self.value
        return None
n_acceptors=5; quorum=3
acceptors=[Acceptor(i) for i in range(n_acceptors)]
p1=Proposer(1,"value_A"); p2=Proposer(2,"value_B")
print("Paxos Consensus:")
r1=p1.propose(acceptors,quorum); print(f"  Proposer 1 ('value_A'): {'decided '+r1 if r1 else 'failed'}")
r2=p2.propose(acceptors,quorum); print(f"  Proposer 2 ('value_B'): {'decided '+r2 if r2 else 'failed'}")
print(f"\nAccepted values: {[a.accepted_v for a in acceptors]}")
