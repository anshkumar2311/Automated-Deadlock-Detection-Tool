class Process:
    def __init__(self, pid, allocated=None, requested=None, max_need=None):
        self.pid = pid
        self.allocated = allocated if allocated else []
        self.requested = requested if requested else []
        self.max_need = max_need if max_need else []
        
    def to_dict(self):
        return {
            'pid': self.pid,
            'allocated': self.allocated,
            'requested': self.requested,
            'max_need': self.max_need
        }
    
    def __repr__(self):
        return f"Process(pid={self.pid}, allocated={self.allocated}, requested={self.requested})"
    
    def __eq__(self, other):
        if isinstance(other, Process):
            return self.pid == other.pid
        return False
    
    def __hash__(self):
        return hash(self.pid)
