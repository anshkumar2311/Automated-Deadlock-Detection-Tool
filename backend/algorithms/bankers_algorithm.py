class BankersAlgorithm:
    def __init__(self, system_state):
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
        processes = self.system_state.get_all_processes()
        resources = self.system_state.get_all_resources()

        if not processes or not resources:
            return None

        rids = [r.rid for r in resources]
        total = {r.rid: r.instances for r in resources}

        allocation = {}
        max_need   = {}
        need       = {}

        for p in processes:
            alloc = {rid: p.allocated.count(rid) for rid in rids}
            allocation[p.pid] = alloc

            if p.max_need:
                mx = {rid: p.max_need.count(rid) for rid in rids}
            else:
                # Fall back: treat requested as remaining need
                mx = {rid: alloc[rid] + p.requested.count(rid) for rid in rids}
            max_need[p.pid] = mx

            nd = {rid: mx[rid] - alloc[rid] for rid in rids}
            # Clamp negative need to 0 (allocation should never exceed max)
            nd = {rid: max(0, v) for rid, v in nd.items()}
            need[p.pid] = nd

        # Available = Total - sum of all allocations
        available = {}
        for rid in rids:
            allocated_sum = sum(allocation[p.pid][rid] for p in processes)
            available[rid] = total[rid] - allocated_sum
            # Guard against negative available (over-allocated input)
            available[rid] = max(0, available[rid])

        return {
            'processes': processes,
            'rids': rids,
            'allocation': allocation,
            'max_need': max_need,
            'need': need,
            'available': available,
        }

    def _need_le_work(self, need_row, work, rids):
        """Return True only if need_row[rid] <= work[rid] for ALL resources."""
        return all(need_row[rid] <= work.get(rid, 0) for rid in rids)

    def is_safe_state(self):
        matrices = self._build_matrices()

        if matrices is None:
            return True, [], []

        processes  = matrices['processes']
        rids       = matrices['rids']
        allocation = matrices['allocation']
        need       = matrices['need']
        work       = matrices['available'].copy()
        finish     = {p.pid: False for p in processes}
        safe_sequence = []

        # Banker's safety algorithm
        while True:
            found = False
            for p in processes:
                if not finish[p.pid] and self._need_le_work(need[p.pid], work, rids):
                    # Simulate granting all remaining need and releasing allocation
                    for rid in rids:
                        work[rid] = work.get(rid, 0) + allocation[p.pid][rid]
                    finish[p.pid] = True
                    safe_sequence.append(p.pid)
                    found = True
                    break  # restart scan from beginning

            if not found:
                break  # no eligible process found – stop

        is_safe = all(finish.values())
        unsafe_processes = [pid for pid, done in finish.items() if not done]

        return is_safe, safe_sequence if is_safe else [], unsafe_processes

    def detect_deadlock(self):
        is_safe, safe_sequence, unsafe_processes = self.is_safe_state()

        return {
            'has_deadlock':      not is_safe,
            'safe_sequence':     safe_sequence if is_safe else None,
            'unsafe_processes':  unsafe_processes,
            'is_safe':           is_safe,
            'state':             'safe' if is_safe else 'unsafe',
        }
