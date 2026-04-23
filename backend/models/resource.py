class Resource:
    def __init__(self, rid, instances=1):
        self.rid = rid
        self.instances = instances
        self.available = instances
        
    def allocate(self, amount=1):
        if self.available >= amount:
            self.available -= amount
            return True
        return False
    
    def release(self, amount=1):
        self.available = min(self.available + amount, self.instances)
        
    def to_dict(self):
        return {
            'rid': self.rid,
            'instances': self.instances,
            'available': self.available
        }
    
    def __repr__(self):
        return f"Resource(rid={self.rid}, instances={self.instances}, available={self.available})"
    
    def __eq__(self, other):
        if isinstance(other, Resource):
            return self.rid == other.rid
        return False
    
    def __hash__(self):
        return hash(self.rid)
