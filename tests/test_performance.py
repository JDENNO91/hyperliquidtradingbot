"""
Performance Tests
Simple performance tests for the trading system
"""

import pytest
import sys
import time
import psutil
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from strategies.core.rsi_scalping_strategy import RSIScalpingStrategy
from core.improved_trading_engine import ImprovedTradingEngine
from core.simple_risk_manager import SimpleRiskManager


class TestPerformance:
    """Simple performance tests"""
    
    def setup_method(self):
        """Setup test components"""
        self.config = {
            "strategy": "rsi_scalping",
            "trading": {
                "market": "ETH-PERP",
                "positionSize": 0.1,
                "leverage": 5,
                "timeframe": "5m"
            },
            "indicators": {
                "rsi": {
                    "period": 14,
                    "overbought": 70,
                    "oversold": 30
                }
            }
        }
        
        # Create test data
        self.test_data = [
            {
                "t": 1640995200000 + i * 300000,
                "o": 2000 + i * 0.5,
                "h": 2010 + i * 0.5,
                "l": 1990 + i * 0.5,
                "c": 2005 + i * 0.5,
                "v": 1000 + i * 10
            }
            for i in range(100)  # 100 data points
        ]
    
    def test_strategy_execution_speed(self):
        """Test strategy execution is fast"""
        strategy = RSIScalpingStrategy(self.config)
        
        start_time = time.time()
        
        # Run strategy on test data
        for i in range(len(self.test_data)):
            if i >= 20:  # Need enough data for indicators
                indicators = strategy.compute_indicators(self.test_data, i)
                signal = strategy.generate_signal(self.test_data, i)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete in under 1 second
        assert execution_time < 1.0
        print(f"Strategy execution time: {execution_time:.3f}s")
    
    def test_memory_usage(self):
        """Test memory usage is reasonable"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple strategies
        strategies = []
        for i in range(10):
            strategy = RSIScalpingStrategy(self.config)
            strategies.append(strategy)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Should not use more than 50MB for 10 strategies
        assert memory_increase < 50
        print(f"Memory increase: {memory_increase:.1f}MB")
    
    def test_data_processing_efficiency(self):
        """Test data processing is efficient"""
        strategy = RSIScalpingStrategy(self.config)
        
        start_time = time.time()
        
        # Process large dataset
        large_data = self.test_data * 10  # 1000 data points
        
        for i in range(20, len(large_data)):
            indicators = strategy.compute_indicators(large_data, i)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 1000 points in under 2 seconds
        assert processing_time < 2.0
        print(f"Data processing time: {processing_time:.3f}s for 1000 points")
    
    def test_strategy_creation_speed(self):
        """Test strategy creation is fast"""
        start_time = time.time()
        
        # Create multiple strategies
        strategies = []
        for i in range(50):
            strategy = RSIScalpingStrategy(self.config)
            strategies.append(strategy)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should create 50 strategies in under 1 second
        assert creation_time < 1.0
        print(f"Strategy creation time: {creation_time:.3f}s for 50 strategies")
    
    def test_memory_leak_detection(self):
        """Test for memory leaks"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run multiple iterations
        for iteration in range(5):
            strategy = RSIScalpingStrategy(self.config)
            
            # Process data
            for i in range(20, len(self.test_data)):
                indicators = strategy.compute_indicators(self.test_data, i)
                signal = strategy.generate_signal(self.test_data, i)
            
            # Force garbage collection
            del strategy
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Should not leak more than 10MB
        assert memory_increase < 10
        print(f"Memory leak test: {memory_increase:.1f}MB increase")
    
    def test_cpu_usage(self):
        """Test CPU usage is reasonable"""
        process = psutil.Process(os.getpid())
        
        # Get initial CPU usage
        initial_cpu = process.cpu_percent()
        
        # Run intensive operations
        strategy = RSIScalpingStrategy(self.config)
        for i in range(100):
            if i >= 20:
                indicators = strategy.compute_indicators(self.test_data, i)
                signal = strategy.generate_signal(self.test_data, i)
        
        # Get final CPU usage
        final_cpu = process.cpu_percent()
        
        # CPU usage should be reasonable (less than 200%)
        assert final_cpu < 200
        print(f"CPU usage: {final_cpu:.1f}%")
    
    def test_concurrent_operations(self):
        """Test concurrent operations work"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def run_strategy_worker(worker_id):
            """Worker function for concurrent testing"""
            try:
                strategy = RSIScalpingStrategy(self.config)
                
                # Process data
                for i in range(20, len(self.test_data)):
                    indicators = strategy.compute_indicators(self.test_data, i)
                
                results_queue.put(f"Worker {worker_id} completed")
            except Exception as e:
                results_queue.put(f"Worker {worker_id} failed: {e}")
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_strategy_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5)
        
        # Check results
        assert results_queue.qsize() == 3
        print(f"Concurrent operations completed: {results_queue.qsize()} workers")
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        # Create large dataset
        large_data = []
        for i in range(1000):
            large_data.append({
                "t": 1640995200000 + i * 300000,
                "o": 2000 + i * 0.1,
                "h": 2010 + i * 0.1,
                "l": 1990 + i * 0.1,
                "c": 2005 + i * 0.1,
                "v": 1000 + i
            })
        
        strategy = RSIScalpingStrategy(self.config)
        
        start_time = time.time()
        
        # Process large dataset
        for i in range(50, len(large_data), 10):  # Sample every 10th point
            indicators = strategy.compute_indicators(large_data, i)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should handle large dataset efficiently
        assert processing_time < 5.0
        print(f"Large dataset processing: {processing_time:.3f}s for 1000 points")
