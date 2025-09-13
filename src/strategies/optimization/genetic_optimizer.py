"""
Genetic Algorithm Strategy Optimizer

This module implements a genetic algorithm for optimizing trading strategy parameters.
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result of strategy optimization."""
    best_parameters: Dict[str, Any]
    best_fitness: float
    generation: int
    population_size: int
    convergence_generation: int
    optimization_history: List[float]


class GeneticOptimizer:
    """
    Genetic Algorithm optimizer for trading strategy parameters.
    
    This optimizer uses evolutionary principles to find optimal parameter combinations
    that maximize trading performance metrics like Sharpe ratio or profit factor.
    """
    
    def __init__(self, 
                 population_size: int = 50,
                 generations: int = 100,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 elite_size: int = 5):
        """
        Initialize the genetic optimizer.
        
        Args:
            population_size: Number of individuals in each generation
            generations: Maximum number of generations to evolve
            mutation_rate: Probability of mutation for each gene
            crossover_rate: Probability of crossover between parents
            elite_size: Number of best individuals to preserve
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        
        self.parameter_ranges = {}
        self.fitness_function = None
        self.optimization_history = []
    
    def set_parameter_ranges(self, parameter_ranges: Dict[str, Tuple[float, float]]):
        """
        Set the parameter ranges for optimization.
        
        Args:
            parameter_ranges: Dict mapping parameter names to (min, max) tuples
        """
        self.parameter_ranges = parameter_ranges
    
    def set_fitness_function(self, fitness_function):
        """
        Set the fitness function for evaluating individuals.
        
        Args:
            fitness_function: Function that takes parameters and returns fitness score
        """
        self.fitness_function = fitness_function
    
    def _create_individual(self) -> Dict[str, float]:
        """Create a random individual with parameters within specified ranges."""
        individual = {}
        for param_name, (min_val, max_val) in self.parameter_ranges.items():
            if isinstance(min_val, int) and isinstance(max_val, int):
                individual[param_name] = random.randint(min_val, max_val)
            else:
                individual[param_name] = random.uniform(min_val, max_val)
        return individual
    
    def _create_population(self) -> List[Dict[str, float]]:
        """Create initial population of random individuals."""
        return [self._create_individual() for _ in range(self.population_size)]
    
    def _evaluate_fitness(self, individual: Dict[str, float]) -> float:
        """Evaluate fitness of an individual."""
        if self.fitness_function is None:
            raise ValueError("Fitness function not set")
        
        try:
            return self.fitness_function(individual)
        except Exception as e:
            logger.warning(f"Fitness evaluation failed: {e}")
            return -float('inf')  # Penalize failed evaluations
    
    def _select_parents(self, population: List[Dict[str, float]], 
                       fitness_scores: List[float]) -> List[Dict[str, float]]:
        """Select parents for reproduction using tournament selection."""
        parents = []
        
        for _ in range(self.population_size - self.elite_size):
            # Tournament selection
            tournament_size = 3
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            
            winner_index = tournament_indices[np.argmax(tournament_fitness)]
            parents.append(population[winner_index])
        
        return parents
    
    def _crossover(self, parent1: Dict[str, float], parent2: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Create two offspring through crossover."""
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        child1 = {}
        child2 = {}
        
        for param_name in self.parameter_ranges.keys():
            if random.random() < 0.5:
                child1[param_name] = parent1[param_name]
                child2[param_name] = parent2[param_name]
            else:
                child1[param_name] = parent2[param_name]
                child2[param_name] = parent1[param_name]
        
        return child1, child2
    
    def _mutate(self, individual: Dict[str, float]) -> Dict[str, float]:
        """Apply mutation to an individual."""
        mutated = individual.copy()
        
        for param_name, (min_val, max_val) in self.parameter_ranges.items():
            if random.random() < self.mutation_rate:
                if isinstance(min_val, int) and isinstance(max_val, int):
                    mutated[param_name] = random.randint(min_val, max_val)
                else:
                    # Gaussian mutation
                    current_val = mutated[param_name]
                    noise = random.gauss(0, (max_val - min_val) * 0.1)
                    new_val = current_val + noise
                    new_val = max(min_val, min(max_val, new_val))
                    mutated[param_name] = new_val
        
        return mutated
    
    def optimize(self) -> OptimizationResult:
        """
        Run the genetic algorithm optimization.
        
        Returns:
            OptimizationResult: Best parameters and optimization statistics
        """
        if not self.parameter_ranges:
            raise ValueError("Parameter ranges not set")
        if self.fitness_function is None:
            raise ValueError("Fitness function not set")
        
        logger.info(f"Starting genetic optimization with {self.population_size} individuals for {self.generations} generations")
        
        # Initialize population
        population = self._create_population()
        best_fitness = -float('inf')
        best_individual = None
        convergence_generation = 0
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = [self._evaluate_fitness(ind) for ind in population]
            
            # Track best individual
            generation_best_idx = np.argmax(fitness_scores)
            generation_best_fitness = fitness_scores[generation_best_idx]
            
            if generation_best_fitness > best_fitness:
                best_fitness = generation_best_fitness
                best_individual = population[generation_best_idx].copy()
                convergence_generation = generation
            
            self.optimization_history.append(generation_best_fitness)
            
            # Log progress
            if generation % 10 == 0:
                logger.info(f"Generation {generation}: Best fitness = {generation_best_fitness:.4f}")
            
            # Check for convergence
            if generation > 20:
                recent_improvement = max(self.optimization_history[-20:]) - min(self.optimization_history[-20:])
                if recent_improvement < 0.001:
                    logger.info(f"Converged at generation {generation}")
                    break
            
            # Create next generation
            new_population = []
            
            # Keep elite individuals
            elite_indices = np.argsort(fitness_scores)[-self.elite_size:]
            for idx in elite_indices:
                new_population.append(population[idx].copy())
            
            # Generate offspring
            parents = self._select_parents(population, fitness_scores)
            
            for i in range(0, len(parents), 2):
                if i + 1 < len(parents):
                    child1, child2 = self._crossover(parents[i], parents[i + 1])
                    new_population.extend([self._mutate(child1), self._mutate(child2)])
                else:
                    new_population.append(self._mutate(parents[i]))
            
            population = new_population
        
        logger.info(f"Optimization completed. Best fitness: {best_fitness:.4f}")
        
        return OptimizationResult(
            best_parameters=best_individual,
            best_fitness=best_fitness,
            generation=generation,
            population_size=self.population_size,
            convergence_generation=convergence_generation,
            optimization_history=self.optimization_history
        )
    
    def save_results(self, result: OptimizationResult, filename: str):
        """Save optimization results to JSON file."""
        data = {
            'best_parameters': result.best_parameters,
            'best_fitness': result.best_fitness,
            'generation': result.generation,
            'population_size': result.population_size,
            'convergence_generation': result.convergence_generation,
            'optimization_history': result.optimization_history
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Optimization results saved to {filename}")


def create_bb_rsi_optimizer() -> GeneticOptimizer:
    """Create a genetic optimizer configured for BBRSI strategy."""
    optimizer = GeneticOptimizer(
        population_size=30,
        generations=50,
        mutation_rate=0.15,
        crossover_rate=0.8,
        elite_size=3
    )
    
    # BBRSI parameter ranges
    parameter_ranges = {
        'rsi_period': (5, 30),
        'rsi_overbought': (60, 85),
        'rsi_oversold': (15, 40),
        'bollinger_period': (10, 30),
        'bollinger_std': (1.5, 3.0),
        'adx_period': (10, 25),
        'adx_threshold': (15, 35)
    }
    
    optimizer.set_parameter_ranges(parameter_ranges)
    return optimizer


def create_scalping_optimizer() -> GeneticOptimizer:
    """Create a genetic optimizer configured for Scalping strategy."""
    optimizer = GeneticOptimizer(
        population_size=25,
        generations=40,
        mutation_rate=0.2,
        crossover_rate=0.75,
        elite_size=2
    )
    
    # Scalping parameter ranges
    parameter_ranges = {
        'rsi_period': (5, 20),
        'rsi_overbought': (65, 80),
        'rsi_oversold': (20, 35),
        'bollinger_period': (10, 25),
        'bollinger_std': (1.8, 2.5),
        'adx_period': (8, 20),
        'adx_threshold': (20, 40)
    }
    
    optimizer.set_parameter_ranges(parameter_ranges)
    return optimizer


if __name__ == "__main__":
    # Example usage
    optimizer = create_bb_rsi_optimizer()
    
    # Mock fitness function (replace with actual strategy evaluation)
    def mock_fitness(parameters):
        # This would normally run a backtest with the given parameters
        # and return a performance metric like Sharpe ratio
        return random.random()
    
    optimizer.set_fitness_function(mock_fitness)
    result = optimizer.optimize()
    
    print(f"Best parameters: {result.best_parameters}")
    print(f"Best fitness: {result.best_fitness:.4f}")
