class BankersAlgorithm:
    def __init__(self, system_state):
        if not system_state:
            raise ValueError("System state cannot be None")
        self.system_state = system_state

    def _build_matrices(self):
        """
        Build numeric allocation, max, need, and available vectors.

        For multi-instance resources the frontend sends resource IDs as
        repeated list entries (e.g. ['R1', 'R1'] means 2 units of R1).
        We count occurrences per resource ID to get integer amounts.

        Available = Total instances - sum of all allocations for that resource.
        Need[i]   = Max[i] - Allocation[i]   (per resource)
        """
        try:
            processes = self.system_state.get_all_processes()
            resources = self.system_state.get_all_resources()

            if not processes or not resources:
                return None

            rids = [r.rid for r in resources if r and hasattr(r, 'rid')]
            if not rids:
                return None
                
            total = {}
            for r in resources:
                if r and hasattr(r, 'rid') and hasattr(r, 'instances'):
                    total[r.rid] = max(1, r.instances)  # Ensure at least 1 instance

            allocation = {}
            max_need   = {}
            need       = {}

            for p in processes:
                if not p or not hasattr(p, 'pid'):
                    continue
                    
                # Safe access to process attributes
                allocated_list = getattr(p, 'allocated', []) or []
                requested_list = getattr(p, 'requested', []) or []
                max_need_list = getattr(p, 'max_need', []) or []
                
                # Count occurrences safely
                alloc = {}
                for rid in rids:
                    alloc[rid] = allocated_list.count(rid) if isinstance(allocated_list, list) else 0
                allocation[p.pid] = alloc

                if max_need_list:
                    mx = {}
                    for rid in rids:
                        mx[rid] = max_need_list.count(rid) if isinstance(max_need_list, list) else 0
                else:
                    # Fall back: treat requested as remaining need
                    mx = {}
                    for rid in rids:
                        req_count = requested_list.count(rid) if isinstance(requested_list, list) else 0
                        mx[rid] = alloc[rid] + req_count
                max_need[p.pid] = mx

                nd = {}
                for rid in rids:
                    nd[rid] = max(0, mx[rid] - alloc[rid])  # Clamp negative need to 0
                need[p.pid] = nd

            # Available = Total - sum of all allocations
            available = {}
            for rid in rids:
                allocated_sum = 0
                for p in processes:
                    if p and hasattr(p, 'pid') and p.pid in allocation:
                        allocated_sum += allocation[p.pid].get(rid, 0)
                available[rid] = max(0, total.get(rid, 0) - allocated_sum)

            return {
                'processes': [p for p in processes if p and hasattr(p, 'pid')],
                'rids': rids,
                'allocation': allocation,
                'max_need': max_need,
                'need': need,
                'available': available,
            }
        except Exception as e:
            # Log error but don't crash
            return None

    def _need_le_work(self, need_row, work, rids):
        """Return True only if need_row[rid] <= work[rid] for ALL resources."""
        try:
            if not isinstance(need_row, dict) or not isinstance(work, dict):
                return False
            return all(need_row.get(rid, 0) <= work.get(rid, 0) for rid in rids)
        except Exception:
            return False

    def is_safe_state(self):
        try:
            matrices = self._build_matrices()

            if matrices is None:
                return True, [], []

            processes  = matrices['processes']
            rids       = matrices['rids']
            allocation = matrices['allocation']
            need       = matrices['need']
            work       = matrices['available'].copy()
            finish     = {p.pid: False for p in processes if p and hasattr(p, 'pid')}
            safe_sequence = []

            # Banker's safety algorithm
            max_iterations = len(processes) * 2  # Prevent infinite loops
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                found = False
                
                for p in processes:
                    if not p or not hasattr(p, 'pid'):
                        continue
                        
                    pid = p.pid
                    if not finish.get(pid, True) and self._need_le_work(need.get(pid, {}), work, rids):
                        # Simulate granting all remaining need and releasing allocation
                        for rid in rids:
                            work[rid] = work.get(rid, 0) + allocation.get(pid, {}).get(rid, 0)
                        finish[pid] = True
                        safe_sequence.append(pid)
                        found = True
                        break  # restart scan from beginning

                if not found:
                    break  # no eligible process found – stop

            is_safe = all(finish.values())
            unsafe_processes = [pid for pid, done in finish.items() if not done]

            return is_safe, safe_sequence if is_safe else [], unsafe_processes
            
        except Exception as e:
            # Return safe defaults on error
            return False, [], []

    def detect_deadlock(self):
        try:
            is_safe, safe_sequence, unsafe_processes = self.is_safe_state()

            return {
                'has_deadlock':      not is_safe,
                'safe_sequence':     safe_sequence if is_safe else None,
                'unsafe_processes':  unsafe_processes,
                'is_safe':           is_safe,
                'state':             'safe' if is_safe else 'unsafe',
            }
        except Exception as e:
            # Return error state
            return {
                'has_deadlock':      False,
                'safe_sequence':     None,
                'unsafe_processes':  [],
                'is_safe':           False,
                'state':             'error',
                'error':             str(e)
            }
