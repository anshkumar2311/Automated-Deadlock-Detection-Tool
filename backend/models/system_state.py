from models.process import Process
from models.resource import Resource

class SystemState:
    def __init__(self):
        self.processes = {}
        self.resources = {}
        
    def add_process(self, process):
        if isinstance(process, Process):
            self.processes[process.pid] = process
        else:
            raise ValueError("Invalid process object")
    
    def add_resource(self, resource):
        if isinstance(resource, Resource):
            self.resources[resource.rid] = resource
        else:
            raise ValueError("Invalid resource object")
    
    def get_process(self, pid):
        return self.processes.get(pid)
    
    def get_resource(self, rid):
        return self.resources.get(rid)
    
    def get_all_processes(self):
        return list(self.processes.values())
    
    def get_all_resources(self):
        return list(self.resources.values())
    
    def to_dict(self):
        return {
            'processes': [p.to_dict() for p in self.processes.values()],
            'resources': [r.to_dict() for r in self.resources.values()]
        }
    
    def __repr__(self):
        return f"SystemState(processes={len(self.processes)}, resources={len(self.resources)})"
