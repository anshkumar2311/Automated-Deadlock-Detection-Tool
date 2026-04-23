class RecoveryStrategy:
    def __init__(self, system_state):
        if not system_state:
            raise ValueError("System state cannot be None")
        self.system_state = system_state
        
    def terminate_process(self, pid):
        try:
            if not pid:
                return False, "Process ID cannot be empty"
                
            process = self.system_state.get_process(pid)
            if not process:
                return False, f"Process {pid} not found"
            
            allocated = getattr(process, 'allocated', []) or []
            if isinstance(allocated, list):
                for resource_id in allocated:
                    if resource_id:
                        resource = self.system_state.get_resource(resource_id)
                        if resource and hasattr(resource, 'release'):
                            try:
                                resource.release(1)
                            except Exception:
                                continue
            
            if hasattr(self.system_state, 'processes') and isinstance(self.system_state.processes, dict):
                if pid in self.system_state.processes:
                    del self.system_state.processes[pid]
            
            return True, f"Process {pid} terminated and resources released"
        except Exception as e:
            return False, f"Failed to terminate process {pid}: {str(e)}"
    
    def preempt_resource(self, pid, resource_id):
        try:
            if not pid or not resource_id:
                return False, "Process ID and resource ID cannot be empty"
                
            process = self.system_state.get_process(pid)
            resource = self.system_state.get_resource(resource_id)
            
            if not process or not resource:
                return False, "Process or resource not found"
            
            allocated = getattr(process, 'allocated', []) or []
            if isinstance(allocated, list) and resource_id in allocated:
                try:
                    allocated.remove(resource_id)
                    if hasattr(resource, 'release'):
                        resource.release(1)
                    return True, f"Resource {resource_id} preempted from process {pid}"
                except Exception as e:
                    return False, f"Failed to preempt resource: {str(e)}"
            
            return False, f"Process {pid} does not hold resource {resource_id}"
        except Exception as e:
            return False, f"Preemption failed: {str(e)}"
    
    def suggest_resolution(self, involved_processes):
        try:
            if not involved_processes or not isinstance(involved_processes, list):
                return {
                    'strategy': 'none',
                    'description': 'No deadlock detected',
                    'actions': []
                }
            
            suggestions = []
            
            for pid in involved_processes:
                if not pid:
                    continue
                    
                try:
                    process = self.system_state.get_process(pid)
                    if process:
                        allocated = getattr(process, 'allocated', []) or []
                        priority = len(allocated) if isinstance(allocated, list) else 0
                        suggestions.append({
                            'action': 'terminate',
                            'target': pid,
                            'priority': priority,
                            'description': f"Terminate process {pid} (holding {priority} resources)"
                        })
                except Exception:
                    continue
            
            suggestions.sort(key=lambda x: x.get('priority', 0))
            
            return {
                'strategy': 'process_termination',
                'description': 'Terminate processes to break deadlock cycle',
                'actions': suggestions
            }
        except Exception as e:
            return {
                'strategy': 'error',
                'description': f'Failed to generate resolution: {str(e)}',
                'actions': []
            }
    
    def apply_priority_based_resolution(self, involved_processes, priorities):
        try:
            if not involved_processes or not isinstance(involved_processes, list):
                return []
            
            process_priorities = {}
            for i, pid in enumerate(involved_processes):
                if pid:
                    priority = priorities.get(pid, i) if isinstance(priorities, dict) else i
                    process_priorities[pid] = priority
            
            sorted_processes = sorted(process_priorities.items(), key=lambda x: x[1])
            
            actions = []
            for pid, priority in sorted_processes[:1]:  # Only terminate one process
                try:
                    success, message = self.terminate_process(pid)
                    actions.append({
                        'pid': pid,
                        'action': 'terminate',
                        'success': success,
                        'message': message
                    })
                except Exception as e:
                    actions.append({
                        'pid': pid,
                        'action': 'terminate',
                        'success': False,
                        'message': f'Error: {str(e)}'
                    })
            
            return actions
        except Exception as e:
            return [{'error': f'Priority-based resolution failed: {str(e)}'}]
