import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.process import Process
from models.resource import Resource
from models.system_state import SystemState
from algorithms.detection_engine import DetectionEngine
from algorithms.rag_builder import RAGBuilder
from algorithms.cycle_detection import CycleDetection

class TestDeadlockDetection(unittest.TestCase):
    
    def test_simple_deadlock(self):
        system_state = SystemState()
        
        r1 = Resource('R1', 1)
        r2 = Resource('R2', 1)
        system_state.add_resource(r1)
        system_state.add_resource(r2)
        
        p1 = Process('P1', allocated=['R1'], requested=['R2'])
        p2 = Process('P2', allocated=['R2'], requested=['R1'])
        system_state.add_process(p1)
        system_state.add_process(p2)
        
        engine = DetectionEngine(system_state)
        result, graph = engine.detect_deadlock()
        
        self.assertTrue(result['deadlock'])
        self.assertGreater(len(result['involved_processes']), 0)
    
    def test_no_deadlock(self):
        system_state = SystemState()
        
        r1 = Resource('R1', 2)
        r2 = Resource('R2', 2)
        system_state.add_resource(r1)
        system_state.add_resource(r2)
        
        p1 = Process('P1', allocated=['R1'], requested=[])
        p2 = Process('P2', allocated=['R2'], requested=[])
        system_state.add_process(p1)
        system_state.add_process(p2)
        
        engine = DetectionEngine(system_state)
        result, graph = engine.detect_deadlock()
        
        self.assertFalse(result['deadlock'])
    
    def test_three_process_deadlock(self):
        system_state = SystemState()
        
        r1 = Resource('R1', 1)
        r2 = Resource('R2', 1)
        r3 = Resource('R3', 1)
        system_state.add_resource(r1)
        system_state.add_resource(r2)
        system_state.add_resource(r3)
        
        p1 = Process('P1', allocated=['R1'], requested=['R2'])
        p2 = Process('P2', allocated=['R2'], requested=['R3'])
        p3 = Process('P3', allocated=['R3'], requested=['R1'])
        system_state.add_process(p1)
        system_state.add_process(p2)
        system_state.add_process(p3)
        
        engine = DetectionEngine(system_state)
        result, graph = engine.detect_deadlock()
        
        self.assertTrue(result['deadlock'])
        self.assertEqual(len(result['involved_processes']), 3)
    
    def test_rag_builder(self):
        system_state = SystemState()
        
        r1 = Resource('R1', 1)
        system_state.add_resource(r1)
        
        p1 = Process('P1', allocated=['R1'], requested=[])
        system_state.add_process(p1)
        
        rag_builder = RAGBuilder(system_state)
        graph = rag_builder.build_graph()
        
        self.assertEqual(graph.number_of_nodes(), 2)
        self.assertGreater(graph.number_of_edges(), 0)
    
    def test_cycle_detection(self):
        system_state = SystemState()
        
        r1 = Resource('R1', 1)
        r2 = Resource('R2', 1)
        system_state.add_resource(r1)
        system_state.add_resource(r2)
        
        p1 = Process('P1', allocated=['R1'], requested=['R2'])
        p2 = Process('P2', allocated=['R2'], requested=['R1'])
        system_state.add_process(p1)
        system_state.add_process(p2)
        
        rag_builder = RAGBuilder(system_state)
        graph = rag_builder.build_graph()
        
        cycle_detector = CycleDetection(graph)
        result = cycle_detector.detect()
        
        self.assertTrue(result['has_deadlock'])
        self.assertGreater(len(result['cycles']), 0)
    
    def test_multiple_instances_no_deadlock(self):
        system_state = SystemState()
        
        r1 = Resource('R1', 3)
        system_state.add_resource(r1)
        
        p1 = Process('P1', allocated=['R1'], requested=[])
        p2 = Process('P2', allocated=['R1'], requested=[])
        system_state.add_process(p1)
        system_state.add_process(p2)
        
        engine = DetectionEngine(system_state)
        result, graph = engine.detect_deadlock()
        
        self.assertFalse(result['deadlock'])

if __name__ == '__main__':
    unittest.main()
