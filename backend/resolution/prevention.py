class PreventionStrategy:
    def __init__(self, system_state):
        self.system_state = system_state
        
    def check_mutual_exclusion(self):
        return {
            'condition': 'Mutual Exclusion',
            'description': 'Resources cannot be shared',
            'prevention': 'Make resources shareable where possible'
        }
    
    def check_hold_and_wait(self):
        processes_holding_and_waiting = []
        
        for process in self.system_state.get_all_processes():
            if process.allocated and process.requested:
                processes_holding_and_waiting.append(process.pid)
        
        return {
            'condition': 'Hold and Wait',
            'description': 'Processes hold resources while waiting for others',
            'prevention': 'Require processes to request all resources at once',
            'violating_processes': processes_holding_and_waiting
        }
    
    def check_no_preemption(self):
        return {
            'condition': 'No Preemption',
            'description': 'Resources cannot be forcibly taken from processes',
            'prevention': 'Allow resource preemption when necessary'
        }
    
    def check_circular_wait(self):
        return {
            'condition': 'Circular Wait',
            'description': 'Circular chain of processes waiting for resources',
            'prevention': 'Impose ordering on resource acquisition'
        }
    
    def analyze_conditions(self):
        return {
            'mutual_exclusion': self.check_mutual_exclusion(),
            'hold_and_wait': self.check_hold_and_wait(),
            'no_preemption': self.check_no_preemption(),
            'circular_wait': self.check_circular_wait()
        }
    
    def suggest_prevention_strategies(self):
        analysis = self.analyze_conditions()
        
        strategies = []
        
        if analysis['hold_and_wait']['violating_processes']:
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
