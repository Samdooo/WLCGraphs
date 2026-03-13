import networkx as nx
from networkx.algorithms import isomorphism
import matplotlib.pyplot as plt

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
    
    def Draw(self):
        nxg = self.GetNxGraph()
        pos = nx.bipartite_layout(nxg, G.left)
        nx.draw(G.GetNxGraph(), pos, with_labels=True, node_color='skyblue', edge_color='gray')
        
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
                    newGraph.left.append(l)
                for r in re:
                    if r not in newGraph.right:
                        newGraph.right.append(r)
                break
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

#################

CRC = CIR(IRC)

G = GameTimes(1, 1) + GameTimes(2, 2) + GameGraph(["a1", "a2", "a3", "a4"], ["b1", "b2"], [("a1", "b1"), ("a2", "b1"), ("a3", "b1"), ("a2", "b2"), ("a3", "b2"), ("a4", "b2")])

#G1 = GameGraph(["a1", "a2"], ["b1", "b2"], [("a1", "b2")])
#G2 = GameGraph(["a1", "a3"], ["b1", "b2"], [("a1", "b2"), ("a3", "b1")])
#G = GameIntersect(G1, G2)

print(G.GetEquivs())

G.Draw()
plt.show()

G = ES(G)
G.Draw()
plt.show()

G = ES(G)
G.Draw()
plt.show()