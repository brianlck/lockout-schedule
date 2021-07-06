from typing import List, Optional, Tuple, Union
from queue import Queue
import math

CostType = Union[int, float]

class Edge:
    """ An edge from u to v in flow network """
    u: int
    v: int
    capacity: int
    cost: CostType
    backward_edge: 'Edge' # backward edge for flow algorithm

    def __init__(self, u: int, v: int, capacity: int, cost: CostType, is_forward: bool = True) -> None:
        self.u = u
        self.v = v
        self.capacity = capacity
        self.cost = cost
        self.is_forward = is_forward
        self.flow = 0
    
    def get_residual_capacity(self) -> CostType:
        return self.capacity - self.flow

    def is_valid(self) -> bool:
        return self.flow >= 0 and self.flow <= self.capacity

    def set_backward_edge(self, backward_edge: 'Edge') -> None:
        self.backward_edge = backward_edge

    def use_edge(self, flow) -> CostType:
        self.flow += flow
        self.backward_edge.flow -= flow
        assert self.is_valid()
        assert self.backward_edge.is_valid()
        return flow * self.cost


class FlowNetwork:
    """ Flow Network implemented with adjacent list """
    nodes: int # number of nodes
    adjacency_list: List[List['Edge']] # Adjacency list of edges
    ran: bool # whether min_cost_max_flow function is ran
    incoming_flow: List[int]

    def __init__(self, nodes) -> None:
        self.nodes = nodes
        self.adjacency_list = [[] for i in range(0, nodes)]
        self.incoming_flow = [0] * nodes
        self.ran = False

    def add_edge(self, u: int, v: int, capacity: int, cost: CostType) -> 'Edge':
        assert u >= 0 and u <= self.nodes
        assert v >= 0 and v <= self.nodes
        assert capacity >= 0
        forward_edge = Edge(u, v, capacity, cost, is_forward=True)
        backward_edge = Edge(v, u, capacity, -cost, is_forward=False)
        backward_edge.flow = capacity
        forward_edge.set_backward_edge(backward_edge)
        backward_edge.set_backward_edge(forward_edge)
        self.adjacency_list[u].append(forward_edge)
        self.adjacency_list[v].append(backward_edge)
        return forward_edge
    
    def get_edges(self) -> List[Edge]:
        return [edge for _ in self.adjacency_list for edge in _]

    def __shortest_path(self, source: int, sink: int) -> Union[bool, Tuple[int, CostType, List[Edge]]]:
        """ Helper function for shortest path in min cost max flow algorithm
            return False if there is no path between source and sink
            return max flow, path cost, path if otherwise
        """
        assert source >= 0 and source <= self.nodes
        assert sink >= 0 and sink <= self.nodes
        distance: List[CostType] = [math.inf] * self.nodes
        parent: List[Optional[Edge]] = [None] * self.nodes
        in_queue: List[bool] = [False] * self.nodes
        spfa_queue: Queue[int] = Queue(maxsize=self.nodes)

        spfa_queue.put(source)
        distance[source] = 0
        while not spfa_queue.empty():
            u = spfa_queue.get()
            in_queue[u] = False
            for edge in self.adjacency_list[u]:
                if not in_queue[edge.v] and edge.flow < edge.capacity and distance[u] + edge.cost < distance[edge.v]:
                    spfa_queue.put(edge.v)
                    in_queue[edge.v] = True
                    parent[edge.v] = edge
                    distance[edge.v] = distance[u] + edge.cost 

        if distance[sink] == math.inf:
            # no path exists
            return False

        max_flow: int = parent[sink].get_residual_capacity()
        current_node: int = sink
        path_edges: List[Edge] = []
        while current_node != source:
            max_flow = min(
                max_flow, parent[current_node].get_residual_capacity())
            path_edges.append(parent[current_node])
            current_node = parent[current_node].u
        return (max_flow, distance[sink], path_edges)

    def min_cost_max_flow(self, source: int, sink: int) -> Tuple[int, CostType]:
        assert source >= 0 and source <= self.nodes
        assert sink >= 0 and sink <= self.nodes
        assert self.ran == False
        max_flow: int = 0
        min_cost: CostType = 0
        while True:
            for _ in self.adjacency_list:
                _.sort(key=lambda edge: self.incoming_flow[edge.v], reverse=True)
            result = self.__shortest_path(source, sink)
            if result == False:
                # No path exists
                break
            flow, cost, edges = result
            max_flow += flow
            for edge in edges:
                min_cost += edge.use_edge(flow)
                self.incoming_flow[edge.v] += flow
        self.ran = True
        return (max_flow, min_cost)
