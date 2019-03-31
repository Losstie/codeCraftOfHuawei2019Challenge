import copy

class Edge() :
    def __init__(self,edge):
        self.weight = {'weight':edge}

    def __getitem__(self, item):
        return self.weight['weight']

    def __setitem__(self, key, value):
        self.weight['weight'] = value


class Node() :

    def __init__(self,node):
        self.node = node
        self.to_ = {}

    def add_to_(self,node,edge):
        self.to_[node]=Edge(edge)

    def __getitem__(self, item):
        return self.to_[item]


class DiGraph():

    def __init__(self):
        self.node ={}
        self.edge =[]
        self.u_edges = {}

    def add_node(self,node):
        self.node[node] =Node(node)

    def add_edge(self,from_,to_,weight):
        self.edge.append([from_,to_,weight])

        if from_ not in self.u_edges.keys():
            self.u_edges[from_] = [(from_,to_)]
        else:
            self.u_edges[from_].append((from_,to_))

        self.node[from_].add_to_(to_,weight)

    @property
    def in_edges(self):
        return [(x[0],x[1]) for x in self.edge]

    # def edges(self,n):
    #     d = {}
    #     for k,v in self.node[n].to_.items():
    #         d[k] = v['weight']
    #     return d

    def edges(self,n):
        return [(i[0],i[1]) for i in self.edge if i[0]==n]

    def __getitem__(self, item):
        return self.node[item]

def dijkstra_path(graph,source, target, weight='weight') :
    start = source
    end = target

    dist = {}
    previous = {}
    for v in graph.node:
        dist[v] = float('inf')
        previous[v] = 'none'
    dist[start] = 0
    u = start
    while u != end:
        u = min(dist, key=dist.get)
        for u, v in graph.u_edges[u]:
            if v in dist:
                alt = dist[u] + graph[u][v]['weight']
                if alt < dist[v]:
                    dist[v] = alt
                    previous[v] = u
        del dist[u]
    path = [end]
    last = end
    while last != start:
        nxt = previous[last]
        path.append(nxt)
        last = nxt
    return list(reversed(path))