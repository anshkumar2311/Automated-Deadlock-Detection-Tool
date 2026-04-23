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


@api.route('/detect', methods=['POST'])
def detect_deadlock():
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response('Request body is missing or not valid JSON.')

        is_valid, errors = InputParser.validate_input(data)
        if not is_valid:
            logger.log_error(f"Validation failed: {errors}")
            return error_response('Input validation failed.', details=errors)

        system_state = InputParser.parse_json_input(data)

        is_valid_state, message = Validator.validate_system_state(system_state)
        if not is_valid_state:
            return error_response(message)

        logger.log_detection_start({
            'processes': len(system_state.get_all_processes()),
            'resources': len(system_state.get_all_resources()),
        })

        detection_engine = DetectionEngine(system_state)
        result, graph = detection_engine.detect_deadlock()

        detection_engine.visualize_graph(graph)

        recovery = RecoveryStrategy(system_state)
        resolution = recovery.suggest_resolution(result['involved_processes'])

        prevention = PreventionStrategy(system_state)
        prevention_strategies = prevention.suggest_prevention_strategies()

        # Build simulation steps
        simulation = _build_simulation(data, result)

        response = {
            'success': True,
            'deadlock': result['deadlock'],
            'involved_processes': result['involved_processes'],
            'cycle_detection': result['cycle_detection'],
            'bankers_algorithm': result['bankers_algorithm'],
            'graph_info': result['graph_info'],
            'resolution': resolution,
            'prevention': prevention_strategies,
            'simulation': simulation,
            'graph_url': '/api/graph',
        }

        logger.log_detection_end(result)
        return jsonify(response), 200

    except ValueError as e:
        logger.log_error('ValueError', e)
        return error_response('Invalid input data. Please review your configuration.')
    except Exception as e:
        logger.log_error('Unexpected error', e)
        return error_response('An unexpected error occurred. Please try again.', status=500)


@api.route('/simulate', methods=['POST'])
def simulate():
    """Return step-by-step simulation data for the given system state."""
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response('Request body is missing or not valid JSON.')

        is_valid, errors = InputParser.validate_input(data)
        if not is_valid:
            return error_response('Input validation failed.', details=errors)

        system_state = InputParser.parse_json_input(data)
        is_valid_state, message = Validator.validate_system_state(system_state)
        if not is_valid_state:
            return error_response(message)

        detection_engine = DetectionEngine(system_state)
        result, _ = detection_engine.detect_deadlock()

        simulation = _build_simulation(data, result)
        return jsonify({'success': True, 'simulation': simulation}), 200

    except Exception as e:
        logger.log_error('Simulate error', e)
        return error_response('Simulation failed.', status=500)


@api.route('/report', methods=['POST'])
def download_report():
    """Generate and return a PDF report."""
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response('Request body is missing or not valid JSON.')

        is_valid, errors = InputParser.validate_input(data)
        if not is_valid:
            return error_response('Input validation failed.', details=errors)

        system_state = InputParser.parse_json_input(data)
        is_valid_state, message = Validator.validate_system_state(system_state)
        if not is_valid_state:
            return error_response(message)

        detection_engine = DetectionEngine(system_state)
        result, graph = detection_engine.detect_deadlock()
        detection_engine.visualize_graph(graph)

        recovery = RecoveryStrategy(system_state)
        resolution = recovery.suggest_resolution(result['involved_processes'])

        prevention = PreventionStrategy(system_state)
        prevention_strategies = prevention.suggest_prevention_strategies()

        full_result = {**result, 'resolution': resolution, 'prevention': prevention_strategies}

        # Resolve graph path relative to this file so it works regardless of CWD
        _here = os.path.dirname(os.path.abspath(__file__))
        graph_path = os.path.join(_here, '..', 'static', 'graph.png')
        graph_path = os.path.normpath(graph_path)

        generator = ReportGenerator()
        pdf_bytes = generator.generate(data, full_result, graph_path=graph_path)

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='deadlock_report.pdf',
        )

    except Exception as e:
        logger.log_error('Report generation error', e)
        return error_response('Report generation failed.', status=500)


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
    steps = []
    processes = data.get('processes', [])
    resources  = data.get('resources', [])
    ba = result.get('bankers_algorithm', {})
    cd = result.get('cycle_detection', {})

    # Step 0 – system initialisation
    res_summary = ', '.join(f"{r['rid']}×{r.get('instances', 1)}" for r in resources)
    steps.append({
        'type': 'init',
        'description': f"System initialised with {len(resources)} resource(s) ({res_summary}) "
                       f"and {len(processes)} process(es).",
        'highlight': [],
        'detail': None,
    })

    # Step 1 – allocations
    for p in processes:
        alloc = p.get('allocated', [])
        if alloc:
            steps.append({
                'type': 'allocation',
                'description': f"{p['pid']} holds: {', '.join(alloc)}",
                'highlight': [p['pid']] + alloc,
                'detail': None,
            })

    # Step 2 – requests
    for p in processes:
        req = p.get('requested', [])
        if req:
            steps.append({
                'type': 'request',
                'description': f"{p['pid']} is waiting for: {', '.join(req)}",
                'highlight': [p['pid']] + req,
                'detail': None,
            })

    # Step 3 – Banker's evaluation
    if ba.get('is_safe'):
        seq = ba.get('safe_sequence') or []
        steps.append({
            'type': 'safe',
            'description': "Banker's Algorithm: safe sequence found — "
                           + ' → '.join(seq),
            'highlight': seq,
            'detail': 'All processes can complete without deadlock.',
        })
    else:
        steps.append({
            'type': 'unsafe',
            'description': "Banker's Algorithm: no safe sequence exists — system is UNSAFE.",
            'highlight': ba.get('unsafe_processes', []),
            'detail': 'Available resources cannot satisfy any waiting process.',
        })

    # Step 4 – cycle detection
    cycles = cd.get('cycles', [])
    if cycles:
        for i, cycle in enumerate(cycles):
            steps.append({
                'type': 'deadlock',
                'description': f"Cycle {i + 1} detected: {' → '.join(str(n) for n in cycle)}",
                'highlight': list(cycle),
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
        steps.append({
            'type': 'verdict_deadlock',
            'description': f"DEADLOCK confirmed. Involved: {', '.join(involved)}",
            'highlight': involved,
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
