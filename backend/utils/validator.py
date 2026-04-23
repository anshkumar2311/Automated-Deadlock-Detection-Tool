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
        if not system_state.get_all_processes():
            return False, "System must have at least one process"

        if not system_state.get_all_resources():
            return False, "System must have at least one resource"

        resource_ids = {r.rid for r in system_state.get_all_resources()}

        for process in system_state.get_all_processes():
            # Validate max_need >= allocation for every resource
            if process.max_need:
                for rid in resource_ids:
                    alloc_count    = process.allocated.count(rid)
                    max_need_count = process.max_need.count(rid)
                    if max_need_count < alloc_count:
                        return (
                            False,
                            f"Process {process.pid}: max_need ({max_need_count}) for "
                            f"resource {rid} is less than allocation ({alloc_count}).",
                        )

            for rid in process.allocated + process.requested + process.max_need:
                if rid not in resource_ids:
                    return False, f"Process {process.pid} references undefined resource {rid}"

        return True, "Valid"

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
