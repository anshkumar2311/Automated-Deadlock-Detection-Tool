import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.process import Process
from models.resource import Resource
from models.system_state import SystemState
from algorithms.bankers_algorithm import BankersAlgorithm
from resolution.recovery import RecoveryStrategy
from resolution.prevention import PreventionStrategy

class TestAlgorithms(unittest.TestCase):
    
    def test_bankers_safe_state(self):
        system_state = SystemState()
        
        r1 = Resource('R1', 10)
        system_state.add_resource(r1)
        
        p1 = Process('P1', allocated=['R1', 'R1'], requested=['R1'], max_need=['R1', 'R1', 'R1'])
        p2 = Process('P2', allocated=['R1'], requested=[], max_need=['R1', 'R1'])
        system_state.add_process(p1)
        system_state.add_process(p2)
        
        bankers = BankersAlgorithm(system_state)
        result = bankers.detect_deadlock()
        
        self.assertFalse(result['has_deadlock'])
        self.assertTrue(result['is_safe'])
    
    def test_bankers_unsafe_state(self):
        system_state = SystemState()
        
        r1 = Resource('R1', 2)
        system_state.add_resource(r1)
        
        p1 = Process('P1', allocated=['R1'], requested=['R1', 'R1'], max_need=['R1', 'R1', 'R1'])
        p2 = Process('P2', allocated=['R1'], requested=['R1'], max_need=['R1', 'R1'])
        system_state.add_process(p1)
        system_state.add_process(p2)
        
        bankers = BankersAlgorithm(system_state)
        result = bankers.detect_deadlock()
        
        self.assertTrue(result['has_deadlock'])
    
    def test_recovery_terminate_process(self):
        system_state = SystemState()
        
        r1 = Resource('R1', 1)
        system_state.add_resource(r1)
        
        p1 = Process('P1', allocated=['R1'], requested=[])
        system_state.add_process(p1)
        
        recovery = RecoveryStrategy(system_state)
        success, message = recovery.terminate_process('P1')
        
        self.assertTrue(success)
        self.assertIsNone(system_state.get_process('P1'))
    
    def test_recovery_preempt_resource(self):
        system_state = SystemState()
        
        r1 = Resource('R1', 1)
        system_state.add_resource(r1)
        
        p1 = Process('P1', allocated=['R1'], requested=[])
        system_state.add_process(p1)
        
        recovery = RecoveryStrategy(system_state)
        success, message = recovery.preempt_resource('P1', 'R1')
        
        self.assertTrue(success)
        self.assertNotIn('R1', p1.allocated)
    
    def test_recovery_suggest_resolution(self):
        system_state = SystemState()
        
        r1 = Resource('R1', 1)
        system_state.add_resource(r1)
        
        p1 = Process('P1', allocated=['R1'], requested=[])
        p2 = Process('P2', allocated=[], requested=['R1'])
        system_state.add_process(p1)
        system_state.add_process(p2)
        
        recovery = RecoveryStrategy(system_state)
        resolution = recovery.suggest_resolution(['P1', 'P2'])
        
        self.assertEqual(resolution['strategy'], 'process_termination')
        self.assertGreater(len(resolution['actions']), 0)
    
    def test_prevention_hold_and_wait(self):
        system_state = SystemState()
        
        r1 = Resource('R1', 1)
        r2 = Resource('R2', 1)
        system_state.add_resource(r1)
        system_state.add_resource(r2)
        
        p1 = Process('P1', allocated=['R1'], requested=['R2'])
        system_state.add_process(p1)
        
        prevention = PreventionStrategy(system_state)
        result = prevention.check_hold_and_wait()
        
        self.assertIn('P1', result['violating_processes'])
    
    def test_prevention_strategies(self):
        system_state = SystemState()
        
        r1 = Resource('R1', 1)
        system_state.add_resource(r1)
        
        p1 = Process('P1', allocated=['R1'], requested=[])
        system_state.add_process(p1)
        
        prevention = PreventionStrategy(system_state)
        strategies = prevention.suggest_prevention_strategies()
        
        self.assertIn('analysis', strategies)
        self.assertIn('strategies', strategies)
        self.assertGreater(len(strategies['strategies']), 0)

if __name__ == '__main__':
    unittest.main()
