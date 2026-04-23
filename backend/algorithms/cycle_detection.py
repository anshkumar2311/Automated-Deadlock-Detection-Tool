import networkx as nx

class CycleDetection:
    def __init__(self, graph):
        if not graph:
            raise ValueError("Graph cannot be None")
        self.graph = graph
        
    def detect_cycle_dfs(self):
        try:
            if not self.graph or self.graph.number_of_nodes() == 0:
                return False, []
                
            visited = set()
            rec_stack = set()
            cycles = []
            
            def dfs(node, path):
                try:
                    visited.add(node)
                    rec_stack.add(node)
                    path.append(node)
                    
                    for neighbor in self.graph.successors(node):
                        if neighbor not in visited:
                            if dfs(neighbor, path.copy()):
                                return True
                        elif neighbor in rec_stack:
                            cycle_start = path.index(neighbor)
                            cycle = path[cycle_start:] + [neighbor]
                            cycles.append(cycle)
                            return True
                    
                    rec_stack.remove(node)
                    return False
                except Exception:
                    return False
            
            for node in self.graph.nodes():
                if node not in visited:
                    try:
                        dfs(node, [])
                    except Exception:
                        continue
            
            return len(cycles) > 0, cycles
        except Exception:
            return False, []
    
    def detect_cycle_networkx(self):
        try:
            if not self.graph or self.graph.number_of_nodes() == 0:
                return False, []
            cycles = list(nx.simple_cycles(self.graph))
            return len(cycles) > 0, cycles
        except Exception:
            return False, []
    
    def get_processes_in_cycles(self, cycles):
        try:
            if not cycles or not isinstance(cycles, list):
                return []
                
            processes = set()
            for cycle in cycles:
                if not isinstance(cycle, list):
                    continue
                for node in cycle:
                    try:
                        node_data = self.graph.nodes.get(node, {})
                        if isinstance(node_data, dict) and node_data.get('node_type') == 'process':
                            processes.add(node)
                    except Exception:
                        continue
            return list(processes)
        except Exception:
            return []
    
    def detect(self):
        try:
            has_cycle, cycles = self.detect_cycle_networkx()
            
            if not has_cycle:
                has_cycle, cycles = self.detect_cycle_dfs()
            
            involved_processes = self.get_processes_in_cycles(cycles) if cycles else []
            
            return {
                'has_deadlock': has_cycle,
                'cycles': cycles or [],
                'involved_processes': involved_processes
            }
        except Exception as e:
            return {
                'has_deadlock': False,
                'cycles': [],
                'involved_processes': [],
                'error': str(e)
            }
