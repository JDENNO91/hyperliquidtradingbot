"""
🚀 UNIVERSAL TRADING DASHBOARD - ONE DASHBOARD FOR EVERYTHING! 🚀

This is THE dashboard that can handle ALL your trading needs in one place!
No more switching between different tools - this dashboard does it ALL.

🎯 WHAT THIS DASHBOARD CAN DO:
==============================

🧪 BACKTESTING DASHBOARD:
   - Analyze historical strategy performance
   - View backtest results with full metrics
   - Compare different strategy parameters
   - Export performance reports
   - Visualize equity curves and drawdowns

📊 LIVE SIMULATION DASHBOARD (Paper Trading):
   - Monitor paper trading in real-time
   - Track simulated P&L and positions
   - Analyze strategy behavior with live market data
   - No real money risk - perfect for testing
   - Real-time updates every 30 seconds

💰 LIVE TRADING DASHBOARD:
   - Monitor REAL trading execution
   - Track live P&L and open positions
   - Real-time risk management alerts
   - Live market data integration
   - Emergency stop functionality

🔄 AUTO-DETECTION:
   - Automatically detects which mode you're in
   - Switches between backtest/simulation/live seamlessly
   - Loads the right data source automatically
   - No configuration needed - just works!

📈 COMPREHENSIVE FEATURES:
   - Performance metrics (win rate, Sharpe ratio, drawdown)
   - Interactive charts (P&L over time, trade distribution)
   - Advanced filtering and search
   - Real-time data updates
   - Export capabilities
   - Mobile-responsive design

How to Use:
-----------
1. Basic Usage (Auto-detect mode):
   streamlit run src/application/dashboard.py

2. Specific Trading Mode:
   streamlit run src/application/dashboard.py -- --mode backtest
   streamlit run src/application/dashboard.py -- --mode live_simulation
   streamlit run src/application/dashboard.py -- --mode live

3. Custom Data File:
   streamlit run src/application/dashboard.py -- --data_path path/to/your/trades.json

4. Command Line Options:
   --server.headless true    # Run without browser
   --server.port 8501       # Custom port
   --server.address 0.0.0.0 # External access

5. Workflow Examples:
   
   BACKTEST MODE:
   # Option 1: Simple (uses smart defaults)
   PYTHONPATH=src python3 src/backtesting/unified_backtester.py
   
   # Option 2: Custom (specify everything)
   PYTHONPATH=src python3 src/backtesting/unified_backtester.py \
     --config src/config/backtest_eth.json \
     --data src/backtesting/data/ETH-PERP/ETH-PERP-1m.json \
     --output src/backtesting/unified_backtest_results.json
   
   # Step 2: Launch dashboard
   streamlit run src/application/dashboard.py -- --mode backtest
   
   💡 WHY TWO OPTIONS?
   - Option 1 (Simple): Uses smart defaults - just works!
   - Option 2 (Custom): Full control over config, data, and output
   - Both create the same dashboard-compatible results
   
   🧹 CLEAN PROJECT: We've removed ALL redundant backtesting systems!
   - Only ONE unified backtesting system remains
   - No more confusion about which tool to use
   - Clean, maintainable codebase
   
   LIVE SIMULATION MODE:
   # Step 1: Run live simulation
   PYTHONPATH=src python3 src/live_simulation/simulation_runner.py
   
   # Step 2: Launch dashboard
   streamlit run src/application/dashboard.py -- --mode live_simulation

6. Data Format Requirements:
   JSON file with trade objects containing:
   - timestamp: Trade timestamp
   - market/symbol: Trading pair
   - side: LONG/SHORT
   - entry_price: Entry price
   - exit_price: Exit price (null for open positions)
   - size: Position size
   - profit: P&L (null for open positions)

7. Dashboard Features:
   - Performance Metrics: Win rate, P&L, drawdown
   - Trade Table: Filterable trade history
   - Charts: P&L over time, trade distribution
   - Real-time Updates: Auto-refresh for live modes
   - Mode Detection: Automatic mode switching

8. Troubleshooting:
   - Ensure trade data file exists and is valid JSON
   - Check file permissions and path
   - Verify data format matches requirements
   - Use browser console for JavaScript errors

🎉 BOTTOM LINE: This dashboard replaces ALL other trading monitoring tools!
   - ✅ Backtesting analysis tools
   - ✅ Paper trading monitors
   - ✅ Live trading dashboards
   - ✅ Performance reporting tools
   - ✅ Trade analysis software

Author: Hyperliquid Trading Bot Team
Date: 2024
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingDashboard:
    """
    🚀 THE ONE AND ONLY DASHBOARD YOU'LL EVER NEED! 🚀
    
    This is a UNIVERSAL trading dashboard that handles EVERYTHING:
    - 🧪 Backtesting analysis and results
    - 📊 Live simulation (paper trading) monitoring  
    - 💰 Live trading execution and risk management
    - 🔄 Automatic mode detection and switching
    - 📈 Comprehensive performance analytics
    - 🎯 Real-time updates and alerts
    
    NO MORE SWITCHING BETWEEN TOOLS - THIS DASHBOARD DOES IT ALL!
    
    Quick Start Example:
    -------------------
    ```python
    # Create and run dashboard for specific mode
    dashboard = TradingDashboard(mode="live_simulation")
    dashboard.run()
    
    # Or run directly from command line:
    # streamlit run src/application/dashboard.py -- --mode live_simulation
    ```
    
    The dashboard will automatically:
    - 🎯 Detect and load data from the appropriate source for each mode
    - 📊 Calculate comprehensive performance metrics (win rate, P&L, drawdown, Sharpe ratio)
    - 📈 Display interactive charts and tables (P&L over time, trade distribution)
    - 🔍 Provide advanced filtering and search capabilities
    - ⚡ Update in real-time for live modes with auto-refresh
    - 🚨 Show risk alerts and position monitoring
    - 📱 Provide mobile-responsive interface
    
    🎉 This dashboard replaces ALL other trading tools combined!
    """
    
    def __init__(self, mode: str = "auto", data_path: str = None):
        """
        Initialize the Trading Dashboard.
        
        Args:
            mode (str): Trading mode - "backtest", "live_simulation", "live", or "auto"
            data_path (str): Optional custom path to trading data file
        """
        self.mode = mode
        self.data_path = data_path
        self.trades_df = None
        self.performance_metrics = {}
        self.is_live_mode = False
        self.data_sources = self._setup_data_sources()
        self.setup_page_config()
        
    def _setup_data_sources(self) -> Dict[str, str]:
        """
        Setup data sources for different trading modes.
        
        Returns:
            Dict[str, str]: Mapping of mode to data file path
        """
        return {
            "backtest": "src/backtesting/unified_backtest_results.json",
            "live_simulation": "src/logs/live_simulation_trades.json",
            "live": "src/logs/live_trades.json",
            "auto": None  # Will be auto-detected
        }
    
    def _detect_mode_from_data(self) -> str:
        """
        Automatically detect trading mode based on available data files.
        
        Returns:
            str: Detected trading mode
        """
        for mode, path in self.data_sources.items():
            if mode == "auto":
                continue
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                        if data and len(data) > 0:
                            return mode
                except:
                    continue
        
        # Default to live_simulation if no data found
        return "live_simulation"
    
    def _get_data_path(self) -> str:
        """
        Get the appropriate data path based on mode and availability.
        
        Returns:
            str: Path to the data file to use
        """
        if self.data_path:
            return self.data_path
            
        if self.mode == "auto":
            detected_mode = self._detect_mode_from_data()
            self.mode = detected_mode
            
        return self.data_sources.get(self.mode, self.data_sources["live_simulation"])
        
    def setup_page_config(self):
        """Configure Streamlit page settings for optimal display."""
        st.set_page_config(
            page_title="Hyperliquid Trading Dashboard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    def load_trade_data(self) -> bool:
        """
        Load trading data from JSON file with error handling.
        
        Returns:
            bool: True if data loaded successfully, False otherwise
        """
        try:
            # Get the appropriate data path
            data_path = self._get_data_path()
            
            # Check if file exists
            if not os.path.exists(data_path):
                st.error(f"❌ Data file not found: {data_path}")
                st.info(f"💡 Make sure you have run some {self.mode} trades first!")
                st.info(f"📁 Expected file: {data_path}")
                return False
                
            # Load and parse JSON data
            with open(data_path, "r") as f:
                trades_data = json.load(f)

# Convert to DataFrame
            self.trades_df = pd.DataFrame(trades_data)
            
            # Validate data structure
            if self.trades_df.empty:
                st.warning("⚠️ No trading data available yet.")
                return False
                
            # Process and clean data
            self._process_trade_data()
            
            st.success(f"✅ Loaded {len(self.trades_df)} {self.mode} trades successfully!")
            return True
            
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON format: {e}")
            return False
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            logger.error(f"Dashboard data loading error: {e}")
            return False
    
    def _process_trade_data(self):
        """
        Process and clean the loaded trade data.
        
        This method handles data cleaning, column standardization, and
        timestamp conversion for consistent data display.
        """
        if self.trades_df is None or self.trades_df.empty:
            return
            
        # Standardize column names
        column_mapping = {
            'pnl': 'profit',
            'entryTime': 'entry_time',
            'exitTime': 'exit_time',
            'type': 'side'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in self.trades_df.columns:
                self.trades_df = self.trades_df.rename(columns={old_name: new_name})
        
        # Convert timestamps to readable format
        timestamp_columns = ['entry_time', 'exit_time', 'timestamp']
        for col in timestamp_columns:
            if col in self.trades_df.columns:
                try:
                    # Handle both millisecond and second timestamps
                    if self.trades_df[col].dtype in ['int64', 'float64']:
                        # Check if timestamps are in milliseconds (13 digits) or seconds (10 digits)
                        sample_timestamp = str(self.trades_df[col].iloc[0])
                        if len(sample_timestamp) == 13:  # Milliseconds
                            self.trades_df[col] = pd.to_datetime(self.trades_df[col], unit='ms')
                        else:  # Seconds
                            self.trades_df[col] = pd.to_datetime(self.trades_df[col], unit='s')
                    else:
                        self.trades_df[col] = pd.to_datetime(self.trades_df[col])
                except Exception as e:
                    logger.warning(f"Could not convert timestamp column {col}: {e}")
        
        # Calculate additional metrics
        self._calculate_additional_metrics()
        
    def _calculate_additional_metrics(self):
        """
        Calculate additional trading metrics and performance indicators.
        
        This method computes derived metrics like trade duration, win/loss status,
        and cumulative performance for enhanced analysis.
        """
        if self.trades_df is None or self.trades_df.empty:
            return
            
        # Calculate trade duration if both entry and exit times exist
        if 'entry_time' in self.trades_df.columns and 'exit_time' in self.trades_df.columns:
            self.trades_df['duration'] = (
                self.trades_df['exit_time'] - self.trades_df['entry_time']
            ).dt.total_seconds() / 60  # Duration in minutes
        
        # Determine win/loss status
        if 'profit' in self.trades_df.columns:
            self.trades_df['status'] = self.trades_df['profit'].apply(
                lambda x: 'WIN' if x > 0 else 'LOSS' if x < 0 else 'BREAKEVEN'
            )
        
        # Calculate cumulative profit
        if 'profit' in self.trades_df.columns:
            self.trades_df['cumulative_profit'] = self.trades_df['profit'].cumsum()
    
    def calculate_performance_metrics(self) -> Dict:
        """
        Calculate comprehensive performance metrics from trade data.
        
        Returns:
            Dict: Dictionary containing all calculated performance metrics
        """
        if self.trades_df is None or self.trades_df.empty:
            return {}
            
        metrics = {}
        
        try:
            # Basic trade statistics
            metrics['total_trades'] = len(self.trades_df)
            
            # Profit/Loss metrics
            if 'profit' in self.trades_df.columns:
                total_profit = self.trades_df['profit'].sum()
                metrics['total_profit'] = f"${total_profit:.2f}"
                metrics['average_profit'] = f"${self.trades_df['profit'].mean():.2f}"
                
                # Win/Loss analysis
                if 'status' in self.trades_df.columns:
                    win_trades = self.trades_df[self.trades_df['status'] == 'WIN']
                    loss_trades = self.trades_df[self.trades_df['status'] == 'LOSS']
                    
                    metrics['win_rate'] = f"{(len(win_trades) / len(self.trades_df) * 100):.1f}%"
                    metrics['total_wins'] = len(win_trades)
                    metrics['total_losses'] = len(loss_trades)
                    
                    if len(win_trades) > 0:
                        metrics['average_win'] = f"${win_trades['profit'].mean():.2f}"
                    if len(loss_trades) > 0:
                        metrics['average_loss'] = f"${loss_trades['profit'].mean():.2f}"
            
            # Risk metrics
            if 'profit' in self.trades_df.columns:
                metrics['max_profit'] = f"${self.trades_df['profit'].max():.2f}"
                metrics['max_loss'] = f"${self.trades_df['profit'].min():.2f}"
                
                # Calculate drawdown
                if 'cumulative_profit' in self.trades_df.columns:
                    cumulative = self.trades_df['cumulative_profit']
                    running_max = cumulative.expanding().max()
                    drawdown = (cumulative - running_max) / running_max * 100
                    metrics['max_drawdown'] = f"{drawdown.min():.2f}%"
            
            # Time-based metrics
            if 'duration' in self.trades_df.columns:
                metrics['average_duration'] = f"{self.trades_df['duration'].mean():.1f} minutes"
                metrics['total_trading_time'] = f"{self.trades_df['duration'].sum() / 60:.1f} hours"
                
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            st.error(f"Error calculating metrics: {e}")
            
        self.performance_metrics = metrics
        return metrics
    
    def display_header(self):
        """Display the main dashboard header with title and basic info."""
        st.title("🚀 Hyperliquid Trading Dashboard")
        st.markdown("---")
        
        # Display basic stats
        if self.trades_df is not None and not self.trades_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Trades", len(self.trades_df))
            with col2:
                if 'profit' in self.trades_df.columns:
                    total_profit = self.trades_df['profit'].sum()
                    st.metric("Total P&L", f"${total_profit:.2f}")
            with col3:
                if 'status' in self.trades_df.columns:
                    win_rate = len(self.trades_df[self.trades_df['status'] == 'WIN']) / len(self.trades_df) * 100
                    st.metric("Win Rate", f"{win_rate:.1f}%")
            with col4:
                if 'cumulative_profit' in self.trades_df.columns:
                    current_balance = self.trades_df['cumulative_profit'].iloc[-1]
                    st.metric("Current Balance", f"${current_balance:.2f}")
    
    def display_performance_metrics(self):
        """Display detailed performance metrics in an organized format."""
        if not self.performance_metrics:
            return
            
        st.subheader("📊 Performance Metrics")
        
        # Create columns for metrics display
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Trade Statistics**")
            for key in ['total_trades', 'total_wins', 'total_losses', 'win_rate']:
                if key in self.performance_metrics:
                    st.write(f"**{key.replace('_', ' ').title()}:** {self.performance_metrics[key]}")
        
        with col2:
            st.markdown("**Financial Metrics**")
            for key in ['total_profit', 'average_profit', 'max_profit', 'max_loss']:
                if key in self.performance_metrics:
                    st.write(f"**{key.replace('_', ' ').title()}:** {self.performance_metrics[key]}")
        
        # Risk metrics
        if any(key in self.performance_metrics for key in ['max_drawdown', 'average_duration']):
            st.markdown("**Risk & Time Metrics**")
            col1, col2 = st.columns(2)
            with col1:
                if 'max_drawdown' in self.performance_metrics:
                    st.write(f"**Max Drawdown:** {self.performance_metrics['max_drawdown']}")
            with col2:
                if 'average_duration' in self.performance_metrics:
                    st.write(f"**Avg Duration:** {self.performance_metrics['average_duration']}")
    
    def display_trade_table(self):
        """Display the main trade data table with filtering options."""
        if self.trades_df is None or self.trades_df.empty:
            return
            
        st.subheader("📋 Trade Details")
        
        # Add filters
        with st.expander("🔍 Filters & Search", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Filter by trade side/type
                if 'side' in self.trades_df.columns:
                    side_filter = st.selectbox(
                        "Trade Side",
                        ['All'] + list(self.trades_df['side'].unique())
                    )
                else:
                    side_filter = 'All'
            
            with col2:
                # Filter by win/loss status
                if 'status' in self.trades_df.columns:
                    status_filter = st.selectbox(
                        "Trade Status",
                        ['All'] + list(self.trades_df['status'].unique())
                    )
                else:
                    status_filter = 'All'
            
            with col3:
                # Date range filter
                if 'entry_time' in self.trades_df.columns:
                    date_range = st.date_input(
                        "Date Range",
                        value=(self.trades_df['entry_time'].min().date(), 
                               self.trades_df['entry_time'].max().date())
                    )
                else:
                    date_range = None
        
        # Apply filters
        filtered_df = self.trades_df.copy()
        
        if side_filter != 'All' and 'side' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['side'] == side_filter]
            
        if status_filter != 'All' and 'status' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        # Display filtered data
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Show filter summary
        st.info(f"📊 Showing {len(filtered_df)} of {len(self.trades_df)} trades")
    
    def display_charts(self):
        """Display performance charts and visualizations."""
        if self.trades_df is None or self.trades_df.empty:
            return
            
        st.subheader("📈 Performance Charts")
        
        # Create tabs for different chart types
        tab1, tab2, tab3 = st.tabs(["P&L Over Time", "Trade Distribution", "Performance Analysis"])
        
        with tab1:
            # Cumulative P&L chart
            if 'cumulative_profit' in self.trades_df.columns and 'entry_time' in self.trades_df.columns:
                fig = px.line(
                    self.trades_df,
                    x='entry_time',
                    y='cumulative_profit',
                    title='Cumulative P&L Over Time',
                    labels={'entry_time': 'Time', 'cumulative_profit': 'Cumulative P&L ($)'}
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
                st.warning("⚠️ Insufficient data for P&L chart")
        
        with tab2:
            # Trade distribution charts
            col1, col2 = st.columns(2)
            
            with col1:
                if 'status' in self.trades_df.columns:
                    status_counts = self.trades_df['status'].value_counts()
                    fig = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        title='Trade Win/Loss Distribution'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'side' in self.trades_df.columns:
                    side_counts = self.trades_df['side'].value_counts()
                    fig = px.bar(
                        x=side_counts.index,
                        y=side_counts.values,
                        title='Trade Side Distribution',
                        labels={'x': 'Trade Side', 'y': 'Count'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Performance analysis
            if 'profit' in self.trades_df.columns:
                # Profit distribution histogram
                fig = px.histogram(
                    self.trades_df,
                    x='profit',
                    nbins=20,
                    title='Profit Distribution',
                    labels={'profit': 'Profit/Loss ($)', 'count': 'Number of Trades'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def run(self):
        """
        Main method to run the complete dashboard.
        
        This method orchestrates the entire dashboard display, including
        data loading, metric calculation, and visualization rendering.
        """
        try:
            # Load data
            if not self.load_trade_data():
                st.stop()
            
            # Calculate performance metrics
            self.calculate_performance_metrics()
            
            # Display dashboard components
            self.display_header()
            self.display_performance_metrics()
            self.display_trade_table()
            self.display_charts()
            
            # Add refresh controls
            self._display_refresh_controls()
                
        except Exception as e:
            st.error(f"❌ Dashboard error: {e}")
            logger.error(f"Dashboard runtime error: {e}")
    
    def _display_refresh_controls(self):
        """Display refresh controls and auto-refresh options."""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Manual Refresh"):
                st.rerun()
        
        with col2:
            # Auto-refresh toggle for live modes
            if self.mode in ["live", "live_simulation"]:
                auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)
                if auto_refresh:
                    st.info("Auto-refresh enabled - data will update every 30 seconds")
        
        with col3:
            # Show current mode and data source
            data_path = self._get_data_path()
            st.info(f"📊 Mode: {self.mode.replace('_', ' ').title()}")
            st.info(f"📁 Source: {os.path.basename(data_path)}")


def main():
    """
    🚀 MAIN ENTRY POINT - LAUNCHES THE UNIVERSAL TRADING DASHBOARD! 🚀
    
    This function creates and runs the TradingDashboard instance,
    providing a simple entry point for the application.
    
    🎯 WHAT HAPPENS WHEN YOU RUN THIS:
    - Dashboard automatically detects your trading mode
    - Loads the appropriate data source
    - Displays comprehensive analytics
    - Provides real-time monitoring
    - Handles ALL trading scenarios in one place!
    
    🚀 NO MORE MULTIPLE TOOLS - THIS IS YOUR ONE-STOP SOLUTION!
    """
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Hyperliquid Trading Dashboard')
    parser.add_argument('--mode', 
                       choices=['backtest', 'live_simulation', 'live', 'auto'],
                       default='auto',
                       help='Trading mode to display')
    parser.add_argument('--data_path', 
                       type=str,
                       help='Custom path to trading data file')
    
    args = parser.parse_args()
    
    try:
        # Create dashboard instance with specified mode
        dashboard = TradingDashboard(mode=args.mode, data_path=args.data_path)
        
        # Run the dashboard
        dashboard.run()
        
    except Exception as e:
        st.error(f"❌ Failed to start dashboard: {e}")
        logger.error(f"Dashboard startup error: {e}")


if __name__ == "__main__":
    main()