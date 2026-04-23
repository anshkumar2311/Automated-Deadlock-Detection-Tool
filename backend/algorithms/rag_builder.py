import networkx as nx
from models.system_state import SystemState

class RAGBuilder:
    def __init__(self, system_state):
        self.system_state = system_state
        self.graph = nx.DiGraph()
        
    def build_graph(self):
        self.graph.clear()
        
        for process in self.system_state.get_all_processes():
            self.graph.add_node(process.pid, node_type='process')
        
        for resource in self.system_state.get_all_resources():
            self.graph.add_node(resource.rid, node_type='resource')
        
        for process in self.system_state.get_all_processes():
            for resource_id in process.requested:
                if resource_id in self.system_state.resources:
                    self.graph.add_edge(process.pid, resource_id, edge_type='request')
            
            for resource_id in process.allocated:
                if resource_id in self.system_state.resources:
                    self.graph.add_edge(resource_id, process.pid, edge_type='allocation')
        
        return self.graph
    
    def get_graph(self):
        return self.graph
    
    def get_process_nodes(self):
        return [node for node, data in self.graph.nodes(data=True) if data.get('node_type') == 'process']
    
    def get_resource_nodes(self):
        return [node for node, data in self.graph.nodes(data=True) if data.get('node_type') == 'resource']
    
    def get_edges_by_type(self, edge_type):
        return [(u, v) for u, v, data in self.graph.edges(data=True) if data.get('edge_type') == edge_type]
