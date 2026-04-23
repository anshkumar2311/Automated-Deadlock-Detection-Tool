from models.process import Process
from models.resource import Resource
from models.system_state import SystemState

class InputParser:
    @staticmethod
    def parse_json_input(data):
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary")
        
        if 'processes' not in data or 'resources' not in data:
            raise ValueError("Input must contain 'processes' and 'resources' keys")
        
        system_state = SystemState()
        
        for resource_data in data['resources']:
            if 'rid' not in resource_data:
                raise ValueError("Each resource must have 'rid'")
            
            rid = resource_data['rid']
            instances = resource_data.get('instances', 1)
            
            resource = Resource(rid, instances)
            system_state.add_resource(resource)
        
        for process_data in data['processes']:
            if 'pid' not in process_data:
                raise ValueError("Each process must have 'pid'")
            
            pid = process_data['pid']
            allocated = process_data.get('allocated', [])
            requested = process_data.get('requested', [])
            max_need = process_data.get('max_need', [])
            
            for rid in allocated + requested + max_need:
                if rid not in system_state.resources:
                    raise ValueError(f"Resource {rid} referenced but not defined")
            
            process = Process(pid, allocated, requested, max_need)
            system_state.add_process(process)
        
        return system_state
    
    @staticmethod
    def validate_input(data):
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Input must be a JSON object")
            return False, errors
        
        if 'processes' not in data:
            errors.append("Missing 'processes' field")
        elif not isinstance(data['processes'], list):
            errors.append("'processes' must be an array")
        
        if 'resources' not in data:
            errors.append("Missing 'resources' field")
        elif not isinstance(data['resources'], list):
            errors.append("'resources' must be an array")
        
        if errors:
            return False, errors
        
        resource_ids = set()
        for i, resource in enumerate(data['resources']):
            if not isinstance(resource, dict):
                errors.append(f"Resource at index {i} must be an object")
                continue
            
            if 'rid' not in resource:
                errors.append(f"Resource at index {i} missing 'rid'")
            else:
                resource_ids.add(resource['rid'])
            
            if 'instances' in resource and not isinstance(resource['instances'], int):
                errors.append(f"Resource {resource.get('rid', i)} 'instances' must be an integer")
        
        for i, process in enumerate(data['processes']):
            if not isinstance(process, dict):
                errors.append(f"Process at index {i} must be an object")
                continue
            
            if 'pid' not in process:
                errors.append(f"Process at index {i} missing 'pid'")
            
            for field in ['allocated', 'requested', 'max_need']:
                if field in process:
                    if not isinstance(process[field], list):
                        errors.append(f"Process {process.get('pid', i)} '{field}' must be an array")
                    else:
                        for rid in process[field]:
                            if rid not in resource_ids:
                                errors.append(f"Process {process.get('pid', i)} references undefined resource '{rid}'")
        
        return len(errors) == 0, errors
