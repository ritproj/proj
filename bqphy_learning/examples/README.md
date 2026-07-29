# BQPhy Python Library - Sample Scripts

This folder contains comprehensive examples demonstrating various optimization scenarios using the BQPhy Python library. Each script showcases different problem types and optimization techniques.

## 📋 Available Examples

### 🌐 Continuous Optimization

#### `continuous_sphere.py`
- **Problem**: Sphere function minimization
- **Type**: Unconstrained continuous optimization
- **Difficulty**: ⭐ Beginner
- **Features**: Simple unimodal function, good for algorithm validation
- **Usage**: `python continuous_sphere.py`

#### `continuous_rastrigin.py`
- **Problem**: Rastrigin function minimization  
- **Type**: Multi-modal continuous optimization
- **Difficulty**: ⭐⭐⭐ Advanced
- **Features**: Highly multi-modal with many local optima
- **Usage**: `python continuous_rastrigin.py`

### 🔢 Binary Optimization

#### `binary_knapsack.py`
- **Problem**: 0-1 Knapsack problem
- **Type**: Combinatorial optimization
- **Difficulty**: ⭐⭐ Intermediate
- **Features**: Classic discrete optimization with constraints
- **Usage**: `python binary_knapsack.py`

### ⚙️ Constrained Optimization

#### `constrained_pressure_vessel.py`
- **Problem**: Pressure vessel design
- **Type**: Engineering design with constraints
- **Difficulty**: ⭐⭐⭐ Advanced
- **Features**: Multiple engineering constraints, penalty methods
- **Usage**: `python constrained_pressure_vessel.py`

## 🚀 Quick Start

1. **Install the BQPhy package**:
   ```bash
   pip install path/to/bqphy-*.whl
   ```

2. **Run any example**:
   ```bash
   cd Sample
   python continuous_sphere.py
   ```

3. **Modify parameters**: Each script has clearly marked configuration sections where you can adjust:
   - Problem dimensions
   - Algorithm parameters
   - Optimization settings

## 📚 Learning Path

### Beginner → Intermediate → Advanced

1. **Start with**: `continuous_sphere.py`
   - Learn basic BQPhy usage
   - Understand configuration parameters
   - See simple optimization in action

2. **Progress to**: `binary_knapsack.py`
   - Explore discrete optimization
   - Learn constraint handling
   - Understand problem formulation

3. **Advance to**: `continuous_rastrigin.py`
   - Tackle multi-modal challenges
   - Learn about convergence issues
   - Explore parameter tuning

4. **Master with**: `constrained_pressure_vessel.py`
   - Handle complex real-world problems
   - Combine multiple techniques
   - Understand advanced concepts

## 🔧 Common Configuration Parameters

All examples use similar configuration structures:

```python
config = {
    "typeOfOptimisation": "continuous",         # continuous, binary, mixed
    "designVariables": 10,                      # Number of design variables
    "lowerBounds": [-10.0] * 10,                # Lower bounds for each variable
    "upperBounds": [10.0] * 10,                 # Upper bounds for each variable
    "maxGeneration": 100,                       # Maximum optimization iterations
    "numPopulation": 50                         # Algorithm population size
}
```

## 🎯 Problem Types Covered

| Problem Class | Example | Real-World Applications |
|---------------|---------|------------------------|
| **Unconstrained Continuous** | Sphere, Rastrigin | Parameter tuning, signal processing |
| **Combinatorial** | Knapsack | Resource allocation, scheduling |
| **Constrained** | Pressure vessel | Engineering design, safety systems |

## 🛠️ Customization Tips

### Modify Objective Functions
```python
def your_custom_function(x):
    # Your optimization logic here
    return objective_value
```

### Adjust Algorithm Parameters
- **Population Size**: Larger for complex problems (50-200)
- **Generations**: More for difficult problems (100-1000)
- **Bounds**: Set realistic ranges for your variables

### Handle Constraints
```python
def constrained_fitness(x):
    objective = your_objective(x)
    penalty = 0
    
    # Add penalty for constraint violations
    if constraint_violated(x):
        penalty += large_number * violation_magnitude
    
    return objective + penalty
```

## 📊 Performance Expectations

| Problem Type | Typical Convergence | Recommended Settings |
|-------------|-------------------|-------------------|
| **Simple Continuous** | 10-50 generations | Pop: 30, Gen: 100 |
| **Multi-modal** | 50-200 generations | Pop: 50, Gen: 200 |
| **Binary** | 20-100 generations | Pop: 40, Gen: 150 |
| **Constrained** | 100-500 generations | Pop: 60, Gen: 300 |

## 🐛 Troubleshooting

### Common Issues and Solutions

1. **Slow Convergence**
   - Increase population size
   - Adjust bounds to reasonable ranges
   - Check objective function scaling

2. **Constraint Violations**
   - Increase penalty weights
   - Check constraint formulation
   - Verify bounds are feasible

3. **Poor Solution Quality**
   - Increase number of generations
   - Try different random seeds
   - Review problem formulation

## 📖 Further Reading

- **BQPhy Documentation**: Comprehensive API reference
- **Optimization Theory**: Books on evolutionary algorithms
- **Problem-Specific Resources**: Domain expertise for your application

## 🤝 Contributing

Found a bug or have an improvement idea?
- Check existing examples for patterns
- Follow the established code style
- Include clear documentation
- Add meaningful test cases

---

**Happy Optimizing with BQPhy! 🚀**