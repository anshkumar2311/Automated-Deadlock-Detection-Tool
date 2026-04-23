class RecoveryStrategy:
    def __init__(self, system_state):
        self.system_state = system_state
        
    def terminate_process(self, pid):
        process = self.system_state.get_process(pid)
        if not process:
            return False, f"Process {pid} not found"
        
        for resource_id in process.allocated:
            resource = self.system_state.get_resource(resource_id)
            if resource:
                resource.release(1)
        
        del self.system_state.processes[pid]
        
        return True, f"Process {pid} terminated and resources released"
    
    def preempt_resource(self, pid, resource_id):
        process = self.system_state.get_process(pid)
        resource = self.system_state.get_resource(resource_id)
        
        if not process or not resource:
            return False, "Process or resource not found"
        
        if resource_id in process.allocated:
            process.allocated.remove(resource_id)
            resource.release(1)
            return True, f"Resource {resource_id} preempted from process {pid}"
        
        return False, f"Process {pid} does not hold resource {resource_id}"
    
    def suggest_resolution(self, involved_processes):
        if not involved_processes:
            return {
                'strategy': 'none',
                'description': 'No deadlock detected',
                'actions': []
            }
        
        suggestions = []
        
        for pid in involved_processes:
            process = self.system_state.get_process(pid)
            if process:
                priority = len(process.allocated)
                suggestions.append({
                    'action': 'terminate',
                    'target': pid,
                    'priority': priority,
                    'description': f"Terminate process {pid} (holding {priority} resources)"
                })
        
        suggestions.sort(key=lambda x: x['priority'])
        
        return {
            'strategy': 'process_termination',
            'description': 'Terminate processes to break deadlock cycle',
            'actions': suggestions
        }
    
    def apply_priority_based_resolution(self, involved_processes, priorities):
        if not involved_processes:
            return []
        
        process_priorities = {}
        for i, pid in enumerate(involved_processes):
            process_priorities[pid] = priorities.get(pid, i)
        
        sorted_processes = sorted(process_priorities.items(), key=lambda x: x[1])
        
        actions = []
        for pid, priority in sorted_processes[:1]:
            success, message = self.terminate_process(pid)
            actions.append({
                'pid': pid,
                'action': 'terminate',
                'success': success,
                'message': message
            })
        
        return actions
