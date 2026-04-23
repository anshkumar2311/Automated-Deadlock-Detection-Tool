import networkx as nx

class CycleDetection:
    def __init__(self, graph):
        self.graph = graph
        
    def detect_cycle_dfs(self):
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node, path):
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
        
        for node in self.graph.nodes():
            if node not in visited:
                dfs(node, [])
        
        return len(cycles) > 0, cycles
    
    def detect_cycle_networkx(self):
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return len(cycles) > 0, cycles
        except:
            return False, []
    
    def get_processes_in_cycles(self, cycles):
        processes = set()
        for cycle in cycles:
            for node in cycle:
                node_data = self.graph.nodes.get(node, {})
                if node_data.get('node_type') == 'process':
                    processes.add(node)
        return list(processes)
    
    def detect(self):
        has_cycle, cycles = self.detect_cycle_networkx()
        
        if not has_cycle:
            has_cycle, cycles = self.detect_cycle_dfs()
        
        involved_processes = self.get_processes_in_cycles(cycles) if cycles else []
        
        return {
            'has_deadlock': has_cycle,
            'cycles': cycles,
            'involved_processes': involved_processes
        }
