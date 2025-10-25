"""
Performance tests for the trading system

This module tests performance benchmarks including:
- Strategy execution speed
- Memory usage
- Backtesting performance
- Data processing efficiency
"""

import pytest
import sys
import time
import psutil
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from strategies.core.rsi_scalping_strategy import RSIScalpingStrategy
from backtesting.improved_backtester import ImprovedBacktester


class TestPerformance:
    """Performance tests for trading system"""
    
    def setup_method(self):
        """Setup test configuration and data"""
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
            },
            "backtest": {
                "initialCapital": 10000,
                "tradingFee": 0.001,
                "slippage": 0.0005
            }
        }
        
        # Create large dataset for performance testing
        self.large_dataset = [
            {
                "t": 1640995200000 + i * 300000,  # 5-minute intervals
                "o": 2000 + i * 0.5,
                "h": 2010 + i * 0.5,
                "l": 1990 + i * 0.5,
                "c": 2005 + i * 0.5,
                "v": 1000 + i * 10
            }
            for i in range(10000)  # 10,000 data points
        ]
    
    def test_strategy_execution_speed(self):
        """Test strategy execution speed"""
        strategy = RSIScalpingStrategy(self.config)
        
        # Measure execution time
        start_time = time.time()
        
        # Process large dataset
        for i in range(100, len(self.large_dataset)):
            indicators = strategy.compute_indicators(self.large_dataset, i)
            signal = strategy.generate_signal(self.large_dataset, i)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (5 seconds for 10k points)
        assert execution_time < 5.0, f"Strategy execution too slow: {execution_time:.2f}s"
        
        # Calculate processing rate
        processing_rate = len(self.large_dataset) / execution_time
        assert processing_rate > 1000, f"Processing rate too low: {processing_rate:.0f} points/sec"
    
    def test_memory_usage(self):
        """Test memory usage during backtesting"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run backtest with large dataset
        strategy = RSIScalpingStrategy(self.config)
        backtester = ImprovedBacktester(self.config)
        
        results = backtester.run_backtest(self.large_dataset, strategy)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 100MB for 10k points)
        assert memory_increase < 100, f"Memory usage too high: {memory_increase:.1f}MB"
    
    def test_backtesting_performance(self):
        """Test backtesting engine performance"""
        strategy = RSIScalpingStrategy(self.config)
        backtester = ImprovedBacktester(self.config)
        
        # Measure backtesting time
        start_time = time.time()
        results = backtester.run_backtest(self.large_dataset, strategy)
        end_time = time.time()
        
        backtest_time = end_time - start_time
        
        # Backtesting should complete within reasonable time
        assert backtest_time < 10.0, f"Backtesting too slow: {backtest_time:.2f}s"
        
        # Verify results are generated
        assert "total_trades" in results
        assert "final_capital" in results
        assert results["total_trades"] >= 0
    
    def test_data_processing_efficiency(self):
        """Test data processing efficiency"""
        strategy = RSIScalpingStrategy(self.config)
        
        # Test indicator computation speed
        start_time = time.time()
        
        for i in range(100, min(1000, len(self.large_dataset))):
            indicators = strategy.compute_indicators(self.large_dataset, i)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process 900 data points quickly
        assert processing_time < 1.0, f"Data processing too slow: {processing_time:.2f}s"
        
        # Calculate processing rate
        points_processed = min(1000, len(self.large_dataset)) - 100
        processing_rate = points_processed / processing_time
        assert processing_rate > 500, f"Processing rate too low: {processing_rate:.0f} points/sec"
    
    def test_concurrent_strategy_execution(self):
        """Test concurrent strategy execution"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def run_strategy(strategy_config, data_subset):
            """Run strategy in separate thread"""
            strategy = RSIScalpingStrategy(strategy_config)
            backtester = ImprovedBacktester(strategy_config)
            results = backtester.run_backtest(data_subset, strategy)
            results_queue.put(results)
        
        # Split data into chunks
        chunk_size = len(self.large_dataset) // 4
        chunks = [
            self.large_dataset[i:i + chunk_size] 
            for i in range(0, len(self.large_dataset), chunk_size)
        ]
        
        # Run strategies concurrently
        threads = []
        start_time = time.time()
        
        for chunk in chunks:
            thread = threading.Thread(target=run_strategy, args=(self.config, chunk))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        concurrent_time = end_time - start_time
        
        # Should complete within reasonable time
        assert concurrent_time < 15.0, f"Concurrent execution too slow: {concurrent_time:.2f}s"
        
        # Verify all results were generated
        assert results_queue.qsize() == len(chunks)
    
    def test_large_dataset_performance(self):
        """Test performance with very large dataset"""
        # Create very large dataset (50k points)
        very_large_dataset = [
            {
                "t": 1640995200000 + i * 300000,
                "o": 2000 + i * 0.1,
                "h": 2010 + i * 0.1,
                "l": 1990 + i * 0.1,
                "c": 2005 + i * 0.1,
                "v": 1000 + i
            }
            for i in range(50000)
        ]
        
        strategy = RSIScalpingStrategy(self.config)
        backtester = ImprovedBacktester(self.config)
        
        # Measure performance
        start_time = time.time()
        results = backtester.run_backtest(very_large_dataset, strategy)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should handle large dataset efficiently
        assert processing_time < 30.0, f"Large dataset processing too slow: {processing_time:.2f}s"
        
        # Verify results
        assert "total_trades" in results
        assert results["total_trades"] >= 0
    
    def test_memory_leak_detection(self):
        """Test for memory leaks during extended execution"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        strategy = RSIScalpingStrategy(self.config)
        
        # Run multiple iterations
        for iteration in range(10):
            for i in range(100, min(1000, len(self.large_dataset))):
                indicators = strategy.compute_indicators(self.large_dataset, i)
                signal = strategy.generate_signal(self.large_dataset, i)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (no significant leaks)
        assert memory_increase < 50, f"Potential memory leak: {memory_increase:.1f}MB increase"
    
    def test_cpu_usage(self):
        """Test CPU usage during execution"""
        process = psutil.Process(os.getpid())
        
        # Monitor CPU usage during execution
        start_time = time.time()
        
        strategy = RSIScalpingStrategy(self.config)
        for i in range(100, min(1000, len(self.large_dataset))):
            indicators = strategy.compute_indicators(self.large_dataset, i)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # CPU usage should be reasonable
        cpu_percent = process.cpu_percent()
        assert cpu_percent < 100, f"CPU usage too high: {cpu_percent}%"
        
        # Execution should be efficient
        assert execution_time < 2.0, f"Execution too slow: {execution_time:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__])
