import networkx as nx
from models.system_state import SystemState

class RAGBuilder:
    def __init__(self, system_state):
        if not system_state:
            raise ValueError("System state cannot be None")
        self.system_state = system_state
        self.graph = nx.DiGraph()
        
    def build_graph(self):
        try:
            self.graph.clear()
            
            # Add process nodes
            processes = self.system_state.get_all_processes()
            if processes:
                for process in processes:
                    if process and hasattr(process, 'pid') and process.pid:
                        self.graph.add_node(process.pid, node_type='process')
            
            # Add resource nodes
            resources = self.system_state.get_all_resources()
            if resources:
                for resource in resources:
                    if resource and hasattr(resource, 'rid') and resource.rid:
                        self.graph.add_node(resource.rid, node_type='resource')
            
            # Add edges
            if processes:
                for process in processes:
                    if not process or not hasattr(process, 'pid') or not process.pid:
                        continue
                        
                    # Request edges (process -> resource)
                    requested = getattr(process, 'requested', []) or []
                    if isinstance(requested, list):
                        for resource_id in requested:
                            if resource_id and resource_id in self.system_state.resources:
                                try:
                                    self.graph.add_edge(process.pid, resource_id, edge_type='request')
                                except Exception:
                                    continue
                    
                    # Allocation edges (resource -> process)
                    allocated = getattr(process, 'allocated', []) or []
                    if isinstance(allocated, list):
                        for resource_id in allocated:
                            if resource_id and resource_id in self.system_state.resources:
                                try:
                                    self.graph.add_edge(resource_id, process.pid, edge_type='allocation')
                                except Exception:
                                    continue
            
            return self.graph
        except Exception as e:
            # Return empty graph on error
            self.graph.clear()
            return self.graph
    
    def get_graph(self):
        return self.graph
    
    def get_process_nodes(self):
        try:
            return [node for node, data in self.graph.nodes(data=True) 
                   if isinstance(data, dict) and data.get('node_type') == 'process']
        except Exception:
            return []
    
    def get_resource_nodes(self):
        try:
            return [node for node, data in self.graph.nodes(data=True) 
                   if isinstance(data, dict) and data.get('node_type') == 'resource']
        except Exception:
            return []
    
    def get_edges_by_type(self, edge_type):
        try:
            return [(u, v) for u, v, data in self.graph.edges(data=True) 
                   if isinstance(data, dict) and data.get('edge_type') == edge_type]
        except Exception:
            return []
