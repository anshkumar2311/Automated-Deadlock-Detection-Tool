class PreventionStrategy:
    def __init__(self, system_state):
        if not system_state:
            raise ValueError("System state cannot be None")
        self.system_state = system_state
        
    def check_mutual_exclusion(self):
        try:
            return {
                'condition': 'Mutual Exclusion',
                'description': 'Resources cannot be shared',
                'prevention': 'Make resources shareable where possible'
            }
        except Exception as e:
            return {
                'condition': 'Mutual Exclusion',
                'description': f'Error checking condition: {str(e)}',
                'prevention': 'Unable to determine prevention strategy'
            }
    
    def check_hold_and_wait(self):
        try:
            processes_holding_and_waiting = []
            
            processes = self.system_state.get_all_processes()
            if processes:
                for process in processes:
                    if not process:
                        continue
                        
                    allocated = getattr(process, 'allocated', []) or []
                    requested = getattr(process, 'requested', []) or []
                    
                    if (isinstance(allocated, list) and len(allocated) > 0 and 
                        isinstance(requested, list) and len(requested) > 0):
                        pid = getattr(process, 'pid', None)
                        if pid:
                            processes_holding_and_waiting.append(pid)
            
            return {
                'condition': 'Hold and Wait',
                'description': 'Processes hold resources while waiting for others',
                'prevention': 'Require processes to request all resources at once',
                'violating_processes': processes_holding_and_waiting
            }
        except Exception as e:
            return {
                'condition': 'Hold and Wait',
                'description': f'Error checking condition: {str(e)}',
                'prevention': 'Unable to determine prevention strategy',
                'violating_processes': []
            }
    
    def check_no_preemption(self):
        try:
            return {
                'condition': 'No Preemption',
                'description': 'Resources cannot be forcibly taken from processes',
                'prevention': 'Allow resource preemption when necessary'
            }
        except Exception as e:
            return {
                'condition': 'No Preemption',
                'description': f'Error checking condition: {str(e)}',
                'prevention': 'Unable to determine prevention strategy'
            }
    
    def check_circular_wait(self):
        try:
            return {
                'condition': 'Circular Wait',
                'description': 'Circular chain of processes waiting for resources',
                'prevention': 'Impose ordering on resource acquisition'
            }
        except Exception as e:
            return {
                'condition': 'Circular Wait',
                'description': f'Error checking condition: {str(e)}',
                'prevention': 'Unable to determine prevention strategy'
            }
    
    def analyze_conditions(self):
        try:
            return {
                'mutual_exclusion': self.check_mutual_exclusion(),
                'hold_and_wait': self.check_hold_and_wait(),
                'no_preemption': self.check_no_preemption(),
                'circular_wait': self.check_circular_wait()
            }
        except Exception as e:
            return {
                'error': f'Analysis failed: {str(e)}',
                'mutual_exclusion': {'condition': 'Error', 'description': 'Analysis failed'},
                'hold_and_wait': {'condition': 'Error', 'description': 'Analysis failed'},
                'no_preemption': {'condition': 'Error', 'description': 'Analysis failed'},
                'circular_wait': {'condition': 'Error', 'description': 'Analysis failed'}
            }
    
    def suggest_prevention_strategies(self):
        try:
            analysis = self.analyze_conditions()
            
            strategies = []
            
            # Check if hold_and_wait analysis succeeded and has violating processes
            hold_wait = analysis.get('hold_and_wait', {})
            violating_processes = hold_wait.get('violating_processes', [])
            
            if isinstance(violating_processes, list) and len(violating_processes) > 0:
                strategies.append({
                    'strategy': 'Eliminate Hold and Wait',
                    'method': 'All-or-nothing resource allocation',
                    'impact': 'Low resource utilization'
                })
            
            strategies.append({
                'strategy': 'Resource Ordering',
                'method': 'Impose total ordering on resource types',
                'impact': 'Prevents circular wait'
            })
            
            strategies.append({
                'strategy': 'Allow Preemption',
                'method': 'Enable resource preemption for lower priority processes',
                'impact': 'May cause process starvation'
            })
            
            return {
                'analysis': analysis,
                'strategies': strategies
            }
        except Exception as e:
            return {
                'error': f'Strategy generation failed: {str(e)}',
                'analysis': {},
                'strategies': [{
                    'strategy': 'Error',
                    'method': 'Unable to generate strategies',
                    'impact': f'Error: {str(e)}'
                }]
            }
