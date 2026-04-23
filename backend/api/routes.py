from flask import Blueprint, request, jsonify, send_file
from utils.input_parser import InputParser
from utils.validator import Validator
from utils.logger import Logger
from algorithms.detection_engine import DetectionEngine
from algorithms.bankers_algorithm import BankersAlgorithm
from resolution.recovery import RecoveryStrategy
from resolution.prevention import PreventionStrategy
from utils.report_generator import ReportGenerator
import os
import io

api = Blueprint('api', __name__)
logger = Logger()


def error_response(message, details=None, status=400):
    body = {'success': False, 'error': message}
    if details:
        body['details'] = details
    return jsonify(body), status


@api.route('/detect', methods=['POST', 'OPTIONS'])
def detect_deadlock():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        logger.log("=== /api/detect called ===")
        logger.log(f"Request method: {request.method}")
        logger.log(f"Request headers: {dict(request.headers)}")
        
        # Get raw request data first
        raw_data = request.get_data()
        logger.log(f"Raw request data length: {len(raw_data) if raw_data else 0}")
        
        # Parse JSON with better error handling
        try:
            data = request.get_json(force=True)
        except Exception as json_error:
            logger.log_error(f"JSON parsing failed: {json_error}")
            return error_response('Invalid JSON format in request body.', status=400)
        
        logger.log(f"Parsed request body: {data}")
        
        # Null/None checks
        if data is None:
            logger.log_error("Request body is None after JSON parsing")
            return error_response('Request body is missing or empty.', status=400)

        if not isinstance(data, dict):
            logger.log_error(f"Request body is not a dict: {type(data)}")
            return error_response('Request body must be a JSON object.', status=400)

        # Check for required fields with detailed logging
        missing_fields = []
        if 'processes' not in data:
            missing_fields.append('processes')
        if 'resources' not in data:
            missing_fields.append('resources')
            
        if missing_fields:
            logger.log_error(f"Missing required fields: {missing_fields}. Available keys: {list(data.keys())}")
            return error_response(f'Request body must contain these fields: {", ".join(missing_fields)}', status=400)

        # Type validation with null checks
        processes = data.get('processes')
        resources = data.get('resources')
        
        if processes is None:
            logger.log_error("'processes' field is null")
            return error_response('"processes" field cannot be null.', status=400)
            
        if resources is None:
            logger.log_error("'resources' field is null")
            return error_response('"resources" field cannot be null.', status=400)

        if not isinstance(processes, list):
            logger.log_error(f"'processes' is not a list: {type(processes)}")
            return error_response('"processes" must be an array.', status=400)

        if not isinstance(resources, list):
            logger.log_error(f"'resources' is not a list: {type(resources)}")
            return error_response('"resources" must be an array.', status=400)

        # Empty array checks
        if len(processes) == 0:
            logger.log_error("Empty processes array")
            return error_response('At least one process is required.', status=400)

        if len(resources) == 0:
            logger.log_error("Empty resources array")
            return error_response('At least one resource is required.', status=400)

        # Validate each process and resource for null values
        for i, process in enumerate(processes):
            if process is None:
                logger.log_error(f"Process at index {i} is null")
                return error_response(f'Process at index {i} cannot be null.', status=400)
            if not isinstance(process, dict):
                logger.log_error(f"Process at index {i} is not a dict: {type(process)}")
                return error_response(f'Process at index {i} must be an object.', status=400)
                
        for i, resource in enumerate(resources):
            if resource is None:
                logger.log_error(f"Resource at index {i} is null")
                return error_response(f'Resource at index {i} cannot be null.', status=400)
            if not isinstance(resource, dict):
                logger.log_error(f"Resource at index {i} is not a dict: {type(resource)}")
                return error_response(f'Resource at index {i} must be an object.', status=400)

        logger.log("Validating input structure...")
        is_valid, errors = InputParser.validate_input(data)
        if not is_valid:
            logger.log_error(f"Validation failed: {errors}")
            return error_response('Input validation failed.', details=errors, status=400)

        logger.log("Parsing JSON input...")
        try:
            system_state = InputParser.parse_json_input(data)
        except Exception as parse_error:
            logger.log_error(f"System state parsing failed: {parse_error}")
            return error_response(f'Failed to parse system state: {str(parse_error)}', status=400)

        logger.log("Validating system state...")
        try:
            is_valid_state, message = Validator.validate_system_state(system_state)
            if not is_valid_state:
                logger.log_error(f"System state validation failed: {message}")
                return error_response(message, status=400)
        except Exception as validation_error:
            logger.log_error(f"System state validation error: {validation_error}")
            return error_response(f'System state validation error: {str(validation_error)}', status=400)

        logger.log_detection_start({
            'processes': len(system_state.get_all_processes()),
            'resources': len(system_state.get_all_resources()),
        })

        logger.log("Creating detection engine...")
        try:
            detection_engine = DetectionEngine(system_state)
        except Exception as engine_error:
            logger.log_error(f"Detection engine creation failed: {engine_error}")
            return error_response(f'Failed to create detection engine: {str(engine_error)}', status=500)
        
        logger.log("Running deadlock detection...")
        try:
            result, graph = detection_engine.detect_deadlock()
        except Exception as detection_error:
            logger.log_error(f"Deadlock detection failed: {detection_error}")
            return error_response(f'Deadlock detection failed: {str(detection_error)}', status=500)

        logger.log("Visualizing graph...")
        try:
            detection_engine.visualize_graph(graph)
        except Exception as viz_error:
            logger.log_error(f"Graph visualization failed: {viz_error}")
            # Don't fail the entire request for visualization errors
            logger.log("Continuing without graph visualization")

        logger.log("Generating recovery strategies...")
        try:
            recovery = RecoveryStrategy(system_state)
            resolution = recovery.suggest_resolution(result.get('involved_processes', []))
        except Exception as recovery_error:
            logger.log_error(f"Recovery strategy generation failed: {recovery_error}")
            resolution = {'actions': [], 'error': 'Failed to generate recovery strategies'}

        logger.log("Generating prevention strategies...")
        try:
            prevention = PreventionStrategy(system_state)
            prevention_strategies = prevention.suggest_prevention_strategies()
        except Exception as prevention_error:
            logger.log_error(f"Prevention strategy generation failed: {prevention_error}")
            prevention_strategies = {'strategies': [], 'error': 'Failed to generate prevention strategies'}

        logger.log("Building simulation steps...")
        try:
            simulation = _build_simulation(data, result)
        except Exception as sim_error:
            logger.log_error(f"Simulation building failed: {sim_error}")
            simulation = [{'type': 'error', 'description': 'Failed to build simulation', 'highlight': [], 'detail': str(sim_error)}]

        response = {
            'success': True,
            'deadlock': result.get('deadlock', False),
            'involved_processes': result.get('involved_processes', []),
            'cycle_detection': result.get('cycle_detection', {}),
            'bankers_algorithm': result.get('bankers_algorithm', {}),
            'graph_info': result.get('graph_info', {}),
            'resolution': resolution,
            'prevention': prevention_strategies,
            'simulation': simulation,
            'graph_url': '/api/graph',
        }

        logger.log_detection_end(result)
        logger.log("=== /api/detect completed successfully ===")
        return jsonify(response), 200

    except ValueError as e:
        logger.log_error('ValueError in /api/detect', e)
        return error_response(f'Invalid input data: {str(e)}', status=400)
    except KeyError as e:
        logger.log_error('KeyError in /api/detect', e)
        return error_response(f'Missing required field: {str(e)}', status=400)
    except Exception as e:
        logger.log_error('Unexpected error in /api/detect', e)
        return error_response(f'An unexpected error occurred: {str(e)}', status=500)


@api.route('/simulate', methods=['POST'])
def simulate():
    """Return step-by-step simulation data for the given system state."""
    try:
        logger.log("=== /api/simulate called ===")
        
        data = request.get_json(silent=True)
        logger.log(f"Request body: {data}")
        
        if not data:
            logger.log_error("Request body is missing or not valid JSON")
            return error_response('Request body is missing or not valid JSON.')

        if not isinstance(data, dict):
            logger.log_error(f"Request body is not a dict: {type(data)}")
            return error_response('Request body must be a JSON object.')

        logger.log("Validating input...")
        is_valid, errors = InputParser.validate_input(data)
        if not is_valid:
            logger.log_error(f"Validation failed: {errors}")
            return error_response('Input validation failed.', details=errors)

        logger.log("Parsing system state...")
        system_state = InputParser.parse_json_input(data)
        
        logger.log("Validating system state...")
        is_valid_state, message = Validator.validate_system_state(system_state)
        if not is_valid_state:
            logger.log_error(f"System state validation failed: {message}")
            return error_response(message)

        logger.log("Running detection for simulation...")
        detection_engine = DetectionEngine(system_state)
        result, _ = detection_engine.detect_deadlock()

        logger.log("Building simulation...")
        simulation = _build_simulation(data, result)
        
        logger.log("=== /api/simulate completed successfully ===")
        return jsonify({'success': True, 'simulation': simulation}), 200

    except ValueError as e:
        logger.log_error('ValueError in /api/simulate', e)
        return error_response(f'Invalid input data: {str(e)}', status=400)
    except KeyError as e:
        logger.log_error('KeyError in /api/simulate', e)
        return error_response(f'Missing required field: {str(e)}', status=400)
    except Exception as e:
        logger.log_error('Unexpected error in /api/simulate', e)
        return error_response(f'Simulation failed: {str(e)}', status=500)


@api.route('/report', methods=['POST'])
def download_report():
    """Generate and return a PDF report."""
    try:
        logger.log("=== /api/report called ===")
        
        data = request.get_json(silent=True)
        logger.log(f"Request body: {data}")
        
        if not data:
            logger.log_error("Request body is missing or not valid JSON")
            return error_response('Request body is missing or not valid JSON.')

        if not isinstance(data, dict):
            logger.log_error(f"Request body is not a dict: {type(data)}")
            return error_response('Request body must be a JSON object.')

        logger.log("Validating input...")
        is_valid, errors = InputParser.validate_input(data)
        if not is_valid:
            logger.log_error(f"Validation failed: {errors}")
            return error_response('Input validation failed.', details=errors)

        logger.log("Parsing system state...")
        system_state = InputParser.parse_json_input(data)
        
        logger.log("Validating system state...")
        is_valid_state, message = Validator.validate_system_state(system_state)
        if not is_valid_state:
            logger.log_error(f"System state validation failed: {message}")
            return error_response(message)

        logger.log("Running detection for report...")
        detection_engine = DetectionEngine(system_state)
        result, graph = detection_engine.detect_deadlock()
        detection_engine.visualize_graph(graph)

        logger.log("Generating recovery strategies...")
        recovery = RecoveryStrategy(system_state)
        resolution = recovery.suggest_resolution(result.get('involved_processes', []))

        logger.log("Generating prevention strategies...")
        prevention = PreventionStrategy(system_state)
        prevention_strategies = prevention.suggest_prevention_strategies()

        full_result = {**result, 'resolution': resolution, 'prevention': prevention_strategies}

        # Resolve graph path relative to this file so it works regardless of CWD
        _here = os.path.dirname(os.path.abspath(__file__))
        graph_path = os.path.join(_here, '..', 'static', 'graph.png')
        graph_path = os.path.normpath(graph_path)

        logger.log(f"Generating PDF report with graph at {graph_path}...")
        generator = ReportGenerator()
        pdf_bytes = generator.generate(data, full_result, graph_path=graph_path)

        logger.log("=== /api/report completed successfully ===")
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='deadlock_report.pdf',
        )

    except ValueError as e:
        logger.log_error('ValueError in /api/report', e)
        return error_response(f'Invalid input data: {str(e)}', status=400)
    except KeyError as e:
        logger.log_error('KeyError in /api/report', e)
        return error_response(f'Missing required field: {str(e)}', status=400)
    except Exception as e:
        logger.log_error('Report generation error in /api/report', e)
        return error_response(f'Report generation failed: {str(e)}', status=500)


@api.route('/sample', methods=['GET'])
def get_sample():
    sample_data = {
        'processes': [
            {'pid': 'P1', 'allocated': ['R1'], 'requested': ['R2'], 'max_need': ['R1', 'R2']},
            {'pid': 'P2', 'allocated': ['R2'], 'requested': ['R1'], 'max_need': ['R1', 'R2']},
        ],
        'resources': [
            {'rid': 'R1', 'instances': 1},
            {'rid': 'R2', 'instances': 1},
        ],
    }
    return jsonify(sample_data), 200


@api.route('/graph', methods=['GET'])
def get_graph():
    _here = os.path.dirname(os.path.abspath(__file__))
    graph_path = os.path.normpath(os.path.join(_here, '..', 'static', 'graph.png'))
    if os.path.exists(graph_path):
        return send_file(graph_path, mimetype='image/png')
    return error_response('Graph not available. Run detection first.', status=404)


@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Deadlock Detection API',
        'version': '2.0.0',
    }), 200


def _build_simulation(data, result):
    """
    Build an ordered list of simulation steps from the raw input + detection result.
    Each step has: type, description, highlight (list of node ids), detail.
    """
    try:
        steps = []
        
        # Validate inputs
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        processes = data.get('processes', [])
        resources = data.get('resources', [])
        
        if not isinstance(processes, list):
            processes = []
        if not isinstance(resources, list):
            resources = []
        
        if not isinstance(result, dict):
            result = {}
            
        ba = result.get('bankers_algorithm', {})
        cd = result.get('cycle_detection', {})

        # Step 0 – system initialisation
        if resources:
            res_summary = ', '.join(
                f"{r.get('rid', '?')}×{r.get('instances', 1)}" 
                for r in resources 
                if isinstance(r, dict) and r.get('rid')
            )
        else:
            res_summary = "none"
            
        steps.append({
            'type': 'init',
            'description': f"System initialised with {len(resources)} resource(s) ({res_summary}) "
                           f"and {len(processes)} process(es).",
            'highlight': [],
            'detail': None,
        })

        # Step 1 – allocations
        for p in processes:
            if not isinstance(p, dict):
                continue
            pid = p.get('pid', '?')
            alloc = p.get('allocated', [])
            if alloc and isinstance(alloc, list) and len(alloc) > 0:
                alloc_str = ', '.join(str(a) for a in alloc if a)
                if alloc_str:
                    steps.append({
                        'type': 'allocation',
                        'description': f"{pid} holds: {alloc_str}",
                        'highlight': [pid] + [str(a) for a in alloc if a],
                        'detail': None,
                    })

        # Step 2 – requests
        for p in processes:
            if not isinstance(p, dict):
                continue
            pid = p.get('pid', '?')
            req = p.get('requested', [])
            if req and isinstance(req, list) and len(req) > 0:
                req_str = ', '.join(str(r) for r in req if r)
                if req_str:
                    steps.append({
                        'type': 'request',
                        'description': f"{pid} is waiting for: {req_str}",
                        'highlight': [pid] + [str(r) for r in req if r],
                        'detail': None,
                    })

        # Step 3 – Banker's evaluation
        if isinstance(ba, dict):
            if ba.get('is_safe'):
                seq = ba.get('safe_sequence', [])
                if isinstance(seq, list) and seq:
                    steps.append({
                        'type': 'safe',
                        'description': "Banker's Algorithm: safe sequence found — "
                                       + ' → '.join(str(s) for s in seq),
                        'highlight': [str(s) for s in seq],
                        'detail': 'All processes can complete without deadlock.',
                    })
                else:
                    steps.append({
                        'type': 'safe',
                        'description': "Banker's Algorithm: system is safe",
                        'highlight': [],
                        'detail': 'All processes can complete without deadlock.',
                    })
            else:
                unsafe_procs = ba.get('unsafe_processes', [])
                steps.append({
                    'type': 'unsafe',
                    'description': "Banker's Algorithm: no safe sequence exists — system is UNSAFE.",
                    'highlight': [str(p) for p in unsafe_procs if p] if isinstance(unsafe_procs, list) else [],
                    'detail': 'Available resources cannot satisfy any waiting process.',
                })

        # Step 4 – cycle detection
        if isinstance(cd, dict):
            cycles = cd.get('cycles', [])
            if cycles and isinstance(cycles, list) and len(cycles) > 0:
                for i, cycle in enumerate(cycles):
                    if isinstance(cycle, list) and cycle:
                        steps.append({
                            'type': 'deadlock',
                            'description': f"Cycle {i + 1} detected: {' → '.join(str(n) for n in cycle)}",
                            'highlight': [str(n) for n in cycle],
                            'detail': 'This circular wait confirms a deadlock.',
                        })
            else:
                steps.append({
                    'type': 'no_cycle',
                    'description': 'No cycles found in the Resource Allocation Graph.',
                    'highlight': [],
                    'detail': None,
                })

        # Step 5 – final verdict
        if result.get('deadlock'):
            involved = result.get('involved_processes', [])
            if isinstance(involved, list):
                involved_str = ', '.join(str(p) for p in involved if p)
                steps.append({
                    'type': 'verdict_deadlock',
                    'description': f"DEADLOCK confirmed. Involved: {involved_str}" if involved_str else "DEADLOCK confirmed.",
                    'highlight': [str(p) for p in involved if p],
                    'detail': 'The system is in a deadlocked state. Manual intervention required.',
                })
            else:
                steps.append({
                    'type': 'verdict_deadlock',
                    'description': 'DEADLOCK confirmed.',
                    'highlight': [],
                    'detail': 'The system is in a deadlocked state. Manual intervention required.',
                })
        else:
            steps.append({
                'type': 'verdict_safe',
                'description': 'System is SAFE. No deadlock detected.',
                'highlight': [],
                'detail': 'All processes will eventually complete execution.',
            })

        return steps
        
    except Exception as e:
        logger = Logger()
        logger.log_error('Error building simulation', e)
        return [{
            'type': 'error',
            'description': 'Failed to build simulation steps',
            'highlight': [],
            'detail': str(e),
        }]
