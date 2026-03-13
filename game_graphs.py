import networkx as nx
from networkx.algorithms import isomorphism
import matplotlib.pyplot as plt
import random

class GameGraph:
    def __init__(self, left, right, edges):
        self.left = left
        self.right = right
        self.edges = edges
    
    def GetNxGraph(self):
        nxg = nx.Graph()
        nxg.add_nodes_from(self.left, bipartite=0)
        nxg.add_nodes_from(self.right, bipartite=1)
        nxg.add_edges_from(self.edges)
        return nxg
        
    def Equals(self, G2):
        return (set(self.left) == set(G2.left)) and (set(self.right) == set(G2.right)) and (set(self.edges) == set(G2.edges))
    
    def GetEquivs(self):
        nxg = self.GetNxGraph()
        newGraph = GameGraph([], [], [])
        
        nm = isomorphism.categorical_node_match("bipartite", 0)
        gm = isomorphism.GraphMatcher(nxg, nxg, node_match=nm)
        automorphisms = list(gm.isomorphisms_iter())
        
        leftEquivs = []
        rightEquivs = []
        visited = set()
        for x in self.left:
            if x in visited:
                continue
            equiv = set()
            for aut in automorphisms:
                equiv.add(aut[x])
                visited.add(aut[x])
            leftEquivs.append(equiv)
        for x in self.right:
            if x in visited:
                continue
            equiv = set()
            for aut in automorphisms:
                equiv.add(aut[x])
                visited.add(aut[x])
            rightEquivs.append(equiv)
        return leftEquivs, rightEquivs
    
    def Draw(self, ax=None, pos=None):
        nxg = self.GetNxGraph()
        if (pos == None):
            pos = nx.bipartite_layout(nxg, self.left)
        nx.draw(nxg, pos, ax=ax, with_labels=True, node_color='skyblue', edge_color='gray')
        
    def __add__(self, G2):
        return GameAdd(self, G2)

def IRC(G: GameGraph):
    nxg = G.GetNxGraph()
    newGraph = GameGraph([], [], [])
    
    for x in G.left:
        dominated = False
        for x2 in G.left:
            n = set(nxg.neighbors(x))
            n2 = set(nxg.neighbors(x2))
            if (n != n2) and (n <= n2):
                dominated = True
                break
        if not dominated:
            newGraph.left.append(x)
    for x in G.right:
        dominated = False
        for x2 in G.right:
            n = set(nxg.neighbors(x))
            n2 = set(nxg.neighbors(x2))
            if (n != n2) and (n <= n2):
                dominated = True
                break
        if not dominated:
            newGraph.right.append(x)
    for e in G.edges:
        if (e[0] in newGraph.left) and (e[1] in newGraph.right):
            newGraph.edges.append(e)
    return newGraph

def ES(G: GameGraph):
    leftEquivs, rightEquivs = G.GetEquivs()
    newGraph = GameGraph([], [], [])
    for le in leftEquivs:
        for re in rightEquivs:
            winning = True
            for l in le:
                for r in re:
                    if (l, r) not in G.edges:
                        winning = False
                        break
                if not winning:
                    break
            if winning:
                for l in le:
                    if l not in newGraph.left:
                        newGraph.left.append(l)
                for r in re:
                    if r not in newGraph.right:
                        newGraph.right.append(r)
    for e in G.edges:
        if e[0] in newGraph.left and e[1] in newGraph.right:
            newGraph.edges.append(e)
    if len(newGraph.left) == 0 or len(newGraph.right) == 0:
        return G
    return newGraph

def GameIntersect(G1: GameGraph, G2: GameGraph):
    G = GameGraph([], [], [])
    for x in G1.left:
        if x in G2.left:
            G.left.append(x)
    for x in G1.right:
        if x in G2.right:
            G.right.append(x)
    for e in G1.edges:
        if e in G2.edges:
            G.edges.append(e)
    return G

def GameAdd(G1: GameGraph, G2: GameGraph, p1="a", p2="b"):
    G = GameGraph([], [], [])
    for x in G1.left:
        G.left.append(p1 + x)
    for x in G2.left:
        G.left.append(p2 + x)
    for x in G1.right:
        G.right.append(p1 + x)
    for x in G2.right:
        G.right.append(p2 + x)
    for e in G1.edges:
        G.edges.append((p1 + e[0], p1 + e[1]))
    for e in G2.edges:
        G.edges.append((p2 + e[0], p2 + e[1]))
    return G

def GameTimes(numLeft: int, numRight: int, pl="a", pr="b"):
    G = GameGraph([], [], [])
    for i in range(numLeft):
        G.left.append(pl + str(i+1))
    for i in range(numRight):
        G.right.append(pr + str(i+1))
    for i in range(numLeft):
        for j in range(numRight):
            G.edges.append((pl + str(i+1), pr + str(j+1)))
    return G

def GameZ(length: int):
    G = GameGraph([], [], [])
    for i in range(length):
        if i % 2 == 0:
            G.left.append(str(i+1))
        else:
            G.right.append(str(i+1))
        if i >= 1:
            G.edges.append((G.left[-1], G.right[-1]))
    return G

def CIR(P):
    def Apply(G):
        old = None
        cur = G
        while (old == None) or (not cur.Equals(old)):
            old = cur
            cur = P(cur)
        return cur
    return Apply

def CAP(P1, P2):
    def Apply(G):
        return GameIntersect(P1(G), P2(G))
    return Apply

def RandomGame(minSide, maxSide, edgeProb):
    l = random.randint(minSide, maxSide)
    r = random.randint(minSide, maxSide)
    left = ["a" + str(i) for i in range(1, l+1)]
    right = ["b" + str(i) for i in range(1, r+1)]
    edges = []
    for i in range(l):
        for j in range(r):
            if (random.random() <= edgeProb):
                edges.append(("a" + str(i+1), "b" + str(j+1)))
    return GameGraph(left, right, edges)

#################

CRC = CIR(IRC)

#P = CAP(CIR(CAP(IRC, ES)), CIR(CAP(CRC, ES)))
P = CAP(IRC, ES)

#its = 0
#while True:
#    G = RandomGame(3, 5, 0.25)
#    Gs = [G]
#    while True:
#        nextG = P(Gs[-1])
#        if not nextG.Equals(Gs[-1]):
#            Gs.append(nextG)
#        else:
#            break
#    #if (len(Gs[-1].left) == 0):
#    #    break
#    if (len(Gs) >= 3):
#        break
#    its += 1
#    print(f"Its: {its}")

# IRC and ES necessary: 
G = GameTimes(1, 1) + GameGraph(["a1", "a2"], ["b1"], [("a1", "b1"), ("a2", "b1")]) + GameGraph(["a1", "a2", "a3"], ["b1", "b2"], [("a1", "b1"), ("a2", "b1"), ("a3", "b1"), ("a2", "b2"), ("a3", "b2")])

#G = GameZ(14)

#G = RandomGame(2, 20, 0.5)

Gs = [G]
while True:
    nextG = P(Gs[-1])
    if not nextG.Equals(Gs[-1]):
        Gs.append(nextG)
    else:
        break
N = len(Gs)

fig, axes = plt.subplots(1, N, figsize=(8, 6))
if N == 1:
    axes = [axes]

pos = nx.bipartite_layout(G.GetNxGraph(), G.left)
for i in range(N):
    Gs[i].Draw(ax=axes[i], pos=pos)
    axes[i].set_title(str(i))
plt.tight_layout()
plt.show()
