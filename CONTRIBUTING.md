# Contributing to Hyperliquid Python Trading Bot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork
3. Create a new branch for your feature
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## 📋 Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

### Testing
- Test all new strategies with backtesting
- Validate on multiple timeframes
- Ensure positive risk-adjusted returns
- Document expected performance

### Documentation
- Update relevant README files
- Add strategy descriptions to configs
- Document any new parameters
- Include usage examples

### Strategy Development
- Place new strategies in `src/strategies/core/`
- Register in `src/strategies/strategy_factory.py`
- Create production config in `src/config/production/`
- Add to `PRODUCTION_STRATEGIES.md` if profitable

### Commits
- Use clear, descriptive commit messages
- One logical change per commit
- Reference issues when applicable

## 🧪 Testing Checklist

Before submitting a new strategy:

- [ ] Backtest on 7+ days of data
- [ ] Test on both ETH-PERP and BTC-PERP
- [ ] Verify positive returns
- [ ] Check max drawdown is acceptable (< 20%)
- [ ] Document win rate and trade frequency
- [ ] Add clear description to config
- [ ] Test timeframe switching works

## 📝 Pull Request Process

1. Update documentation
2. Add tests if applicable
3. Ensure all existing tests pass
4. Describe changes in PR description
5. Wait for review

## ❓ Questions

Open an issue for:
- Bug reports
- Feature requests
- Strategy ideas
- Documentation improvements

## 🎯 Areas for Contribution

- New profitable strategies
- Performance optimizations
- Better risk management
- Real-time data integration
- UI/Dashboard improvements
- Additional indicators
- More comprehensive testing

Thank you for contributing! 🙏

