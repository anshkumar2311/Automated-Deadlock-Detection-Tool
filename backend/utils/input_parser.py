from models.process import Process
from models.resource import Resource
from models.system_state import SystemState

class InputParser:
    @staticmethod
    def parse_json_input(data):
        try:
            if not isinstance(data, dict):
                raise ValueError("Input must be a dictionary")
            
            if 'processes' not in data or 'resources' not in data:
                raise ValueError("Input must contain 'processes' and 'resources' keys")
            
            # Validate data types before processing
            if not isinstance(data['processes'], list):
                raise ValueError("'processes' must be a list")
            
            if not isinstance(data['resources'], list):
                raise ValueError("'resources' must be a list")
            
            system_state = SystemState()
            
            # Process resources first to validate references
            resource_ids = set()
            for i, resource_data in enumerate(data['resources']):
                if not isinstance(resource_data, dict):
                    raise ValueError(f"Resource at index {i} must be a dictionary")
                
                if 'rid' not in resource_data:
                    raise ValueError(f"Resource at index {i} must have 'rid'")
                
                rid = resource_data['rid']
                if not isinstance(rid, str) or not rid.strip():
                    raise ValueError(f"Resource 'rid' at index {i} must be a non-empty string")
                
                instances = resource_data.get('instances', 1)
                if not isinstance(instances, int) or instances < 1:
                    raise ValueError(f"Resource '{rid}' instances must be a positive integer")
                
                if rid in resource_ids:
                    raise ValueError(f"Duplicate resource ID: {rid}")
                
                resource_ids.add(rid)
                resource = Resource(rid, instances)
                system_state.add_resource(resource)
            
            # Process processes and validate resource references
            process_ids = set()
            for i, process_data in enumerate(data['processes']):
                if not isinstance(process_data, dict):
                    raise ValueError(f"Process at index {i} must be a dictionary")
                
                if 'pid' not in process_data:
                    raise ValueError(f"Process at index {i} must have 'pid'")
                
                pid = process_data['pid']
                if not isinstance(pid, str) or not pid.strip():
                    raise ValueError(f"Process 'pid' at index {i} must be a non-empty string")
                
                if pid in process_ids:
                    raise ValueError(f"Duplicate process ID: {pid}")
                
                process_ids.add(pid)
                
                allocated = process_data.get('allocated', [])
                requested = process_data.get('requested', [])
                max_need = process_data.get('max_need', [])
                
                # Validate field types
                for field_name, field_value in [('allocated', allocated), ('requested', requested), ('max_need', max_need)]:
                    if not isinstance(field_value, list):
                        raise ValueError(f"Process '{pid}' field '{field_name}' must be a list")
                    
                    # Validate resource references
                    for rid in field_value:
                        if not isinstance(rid, str):
                            raise ValueError(f"Process '{pid}' field '{field_name}' contains non-string resource ID: {rid}")
                        if rid not in resource_ids:
                            raise ValueError(f"Process '{pid}' references undefined resource '{rid}' in '{field_name}'")
                
                process = Process(pid, allocated, requested, max_need)
                system_state.add_process(process)
            
            return system_state
        
        except Exception as e:
            # Re-raise with more context
            raise ValueError(f"Failed to parse input: {str(e)}")
    
    @staticmethod
    def validate_input(data):
        errors = []
        
        try:
            if not isinstance(data, dict):
                errors.append("Input must be a JSON object")
                return False, errors
            
            if 'processes' not in data:
                errors.append("Missing 'processes' field")
            elif data['processes'] is None:
                errors.append("'processes' field cannot be null")
            elif not isinstance(data['processes'], list):
                errors.append("'processes' must be an array")
            
            if 'resources' not in data:
                errors.append("Missing 'resources' field")
            elif data['resources'] is None:
                errors.append("'resources' field cannot be null")
            elif not isinstance(data['resources'], list):
                errors.append("'resources' must be an array")
            
            if errors:
                return False, errors
            
            # Validate resources
            resource_ids = set()
            for i, resource in enumerate(data['resources']):
                if resource is None:
                    errors.append(f"Resource at index {i} cannot be null")
                    continue
                    
                if not isinstance(resource, dict):
                    errors.append(f"Resource at index {i} must be an object")
                    continue
                
                if 'rid' not in resource:
                    errors.append(f"Resource at index {i} missing 'rid'")
                elif not isinstance(resource['rid'], str) or not resource['rid'].strip():
                    errors.append(f"Resource at index {i} 'rid' must be a non-empty string")
                else:
                    rid = resource['rid']
                    if rid in resource_ids:
                        errors.append(f"Duplicate resource ID: {rid}")
                    else:
                        resource_ids.add(rid)
                
                if 'instances' in resource:
                    instances = resource['instances']
                    if not isinstance(instances, int) or instances < 1:
                        errors.append(f"Resource {resource.get('rid', i)} 'instances' must be a positive integer")
            
            # Validate processes
            process_ids = set()
            for i, process in enumerate(data['processes']):
                if process is None:
                    errors.append(f"Process at index {i} cannot be null")
                    continue
                    
                if not isinstance(process, dict):
                    errors.append(f"Process at index {i} must be an object")
                    continue
                
                if 'pid' not in process:
                    errors.append(f"Process at index {i} missing 'pid'")
                elif not isinstance(process['pid'], str) or not process['pid'].strip():
                    errors.append(f"Process at index {i} 'pid' must be a non-empty string")
                else:
                    pid = process['pid']
                    if pid in process_ids:
                        errors.append(f"Duplicate process ID: {pid}")
                    else:
                        process_ids.add(pid)
                
                for field in ['allocated', 'requested', 'max_need']:
                    if field in process:
                        field_value = process[field]
                        if field_value is None:
                            errors.append(f"Process {process.get('pid', i)} '{field}' cannot be null")
                        elif not isinstance(field_value, list):
                            errors.append(f"Process {process.get('pid', i)} '{field}' must be an array")
                        else:
                            for j, rid in enumerate(field_value):
                                if not isinstance(rid, str):
                                    errors.append(f"Process {process.get('pid', i)} '{field}' item {j} must be a string")
                                elif rid not in resource_ids:
                                    errors.append(f"Process {process.get('pid', i)} references undefined resource '{rid}' in '{field}'")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors
