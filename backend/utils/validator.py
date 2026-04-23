class Validator:
    @staticmethod
    def validate_process_data(process_data):
        if not isinstance(process_data, dict):
            return False, "Process data must be a dictionary"

        if 'pid' not in process_data:
            return False, "Process must have 'pid'"

        if not isinstance(process_data['pid'], str) or not process_data['pid']:
            return False, "Process 'pid' must be a non-empty string"

        for field in ['allocated', 'requested', 'max_need']:
            if field in process_data:
                if not isinstance(process_data[field], list):
                    return False, f"Process '{field}' must be a list"

        return True, "Valid"

    @staticmethod
    def validate_resource_data(resource_data):
        if not isinstance(resource_data, dict):
            return False, "Resource data must be a dictionary"

        if 'rid' not in resource_data:
            return False, "Resource must have 'rid'"

        if not isinstance(resource_data['rid'], str) or not resource_data['rid']:
            return False, "Resource 'rid' must be a non-empty string"

        if 'instances' in resource_data:
            if not isinstance(resource_data['instances'], int) or resource_data['instances'] < 1:
                return False, "Resource 'instances' must be a positive integer"

        return True, "Valid"

    @staticmethod
    def validate_system_state(system_state):
        try:
            if not system_state:
                return False, "System state cannot be null"
            
            processes = system_state.get_all_processes()
            resources = system_state.get_all_resources()
            
            if not processes:
                return False, "System must have at least one process"

            if not resources:
                return False, "System must have at least one resource"

            resource_ids = {r.rid for r in resources}

            for process in processes:
                if not process:
                    return False, f"Process cannot be null"
                
                if not hasattr(process, 'pid') or not process.pid:
                    return False, f"Process must have a valid pid"
                
                # Validate max_need >= allocation for every resource
                if hasattr(process, 'max_need') and process.max_need:
                    for rid in resource_ids:
                        alloc_count = process.allocated.count(rid) if hasattr(process, 'allocated') and process.allocated else 0
                        max_need_count = process.max_need.count(rid) if process.max_need else 0
                        if max_need_count < alloc_count:
                            return (
                                False,
                                f"Process {process.pid}: max_need ({max_need_count}) for "
                                f"resource {rid} is less than allocation ({alloc_count}).",
                            )

                # Validate resource references
                all_refs = []
                if hasattr(process, 'allocated') and process.allocated:
                    all_refs.extend(process.allocated)
                if hasattr(process, 'requested') and process.requested:
                    all_refs.extend(process.requested)
                if hasattr(process, 'max_need') and process.max_need:
                    all_refs.extend(process.max_need)
                
                for rid in all_refs:
                    if rid not in resource_ids:
                        return False, f"Process {process.pid} references undefined resource {rid}"

            return True, "Valid"
            
        except Exception as e:
            return False, f"System state validation error: {str(e)}"

    @staticmethod
    def validate_request(data):
        if not data:
            return False, "Request body is empty"

        if not isinstance(data, dict):
            return False, "Request body must be JSON object"

        for field in ['processes', 'resources']:
            if field not in data:
                return False, f"Missing required field: {field}"

        return True, "Valid"
