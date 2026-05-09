# -*- coding: utf-8 -*-
"""
🌊 KLOUD PRODUCTION AUTO-LEARNING CONNECTOR
===============================================
Lidh Auto-Learning Engine me:
- Mega Signal Integrator (5000+ data sources)
- Hetzner Docker infrastructure
- Real-time signal feeds

Production-grade: CPU/Disk optimized, batch processing

Author: Kloud Team
Version: 1.0.0 Production
"""

import os
import sys
import time
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import threading
import queue

# Add parent and ocean-core to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ocean-core'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class ProductionConfig:
    """Production configuration"""
    # Hetzner API
    hetzner_api_url: str = os.getenv('HETZNER_API_URL', 'http://kloud-api:8000')
    hetzner_external_url: str = os.getenv('HETZNER_EXTERNAL_URL', 'https://api.kloud.com')
    
    # Signal processing
    signal_batch_size: int = 50          # Process 50 signals at a time
    signal_interval_sec: float = 1.0     # Check for signals every 1 sec
    max_signals_per_minute: int = 100    # Rate limit
    
    # Learning
    learning_batch_size: int = 100       # Write to CBOR every 100 entries
    max_memory_entries: int = 1000       # Max entries in RAM
    
    # Source weights (higher = more important)
    source_weights: Dict[str, float] = field(default_factory=lambda: {
        'eeg_neuro': 1.5,
        'scientific': 1.3,
        'finance': 1.2,
        'health': 1.4,
        'news': 1.0,
        'iot': 1.1,
        'environment': 1.2,
    })


# =============================================================================
# SIGNAL BUFFER
# =============================================================================

class SignalBuffer:
    """Thread-safe signal buffer for production"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._buffer: List[Dict] = []
        self._lock = threading.Lock()
        self._stats = {
            'total_received': 0,
            'total_processed': 0,
            'total_dropped': 0,
        }
    
    def push(self, signal: Dict) -> bool:
        """Add signal to buffer"""
        with self._lock:
            if len(self._buffer) >= self.max_size:
                self._buffer.pop(0)  # Remove oldest
                self._stats['total_dropped'] += 1
            
            signal['buffer_time'] = datetime.now(timezone.utc).isoformat()
            self._buffer.append(signal)
            self._stats['total_received'] += 1
            return True
    
    def pop_batch(self, size: int = 50) -> List[Dict]:
        """Pop a batch of signals"""
        with self._lock:
            batch = self._buffer[:size]
            self._buffer = self._buffer[size:]
            self._stats['total_processed'] += len(batch)
            return batch
    
    def size(self) -> int:
        with self._lock:
            return len(self._buffer)
    
    def stats(self) -> Dict:
        with self._lock:
            return {**self._stats, 'buffer_size': len(self._buffer)}


# =============================================================================
# PRODUCTION CONNECTOR
# =============================================================================

class ProductionAutoLearningConnector:
    """
    Production-grade connector:
    - Connects to Mega Signal Integrator
    - Feeds signals to Auto-Learning Engine
    - Runs in Docker on Hetzner
    """
    
    def __init__(self, config: Optional[ProductionConfig] = None):
        self.config = config or ProductionConfig()
        self.signal_buffer = SignalBuffer()
        self.running = False
        
        # Stats
        self.stats = {
            'start_time': None,
            'signals_learned': 0,
            'sources_active': 0,
            'last_signal_time': None,
        }
        
        # Initialize components
        self._init_signal_integrator()
        self._init_auto_learner()
        
        logger.info("✅ Production Auto-Learning Connector initialized")
        logger.info(f"   📡 Hetzner API: {self.config.hetzner_api_url}")
        logger.info(f"   📊 Batch size: {self.config.signal_batch_size}")
    
    def _init_signal_integrator(self):
        """Initialize Mega Signal Integrator"""
        try:
            from mega_signal_integrator import get_mega_signal_integrator
            self.integrator = get_mega_signal_integrator()
            logger.info("✅ Mega Signal Integrator connected")
        except ImportError as e:
            logger.warning(f"⚠️ Mega Signal Integrator not available: {e}")
            self.integrator = None
    
    def _init_auto_learner(self):
        """Initialize Auto-Learning Engine"""
        try:
            from auto_learning_optimized import AutoLearningOptimized
            self.learner = AutoLearningOptimized()
            logger.info("✅ Auto-Learning Engine connected")
        except ImportError as e:
            logger.warning(f"⚠️ Auto-Learning Engine not available: {e}")
            self.learner = None
    
    def _signal_to_question(self, signal: Dict) -> str:
        """Convert signal to learnable question"""
        signal_type = signal.get('type', 'unknown')
        source = signal.get('source', 'unknown')
        data = signal.get('data', {})
        ts = signal.get('timestamp', datetime.now(timezone.utc).isoformat())
        
        # Add timestamp suffix for uniqueness
        ts_suffix = ts[-8:]  # Last 8 chars of timestamp
        
        # Generate intelligent question from signal
        if signal_type == 'news':
            title = data.get('title', 'Unknown news')
            return f"What are the implications of: {title}? [{ts_suffix}]"
        
        elif signal_type == 'finance':
            metric = data.get('metric', 'price')
            value = data.get('value', 0)
            return f"How does {metric} at {value} affect the market? [{ts_suffix}]"
        
        elif signal_type == 'health':
            condition = data.get('condition', 'health event')
            return f"What is the significance of {condition} in public health? [{ts_suffix}]"
        
        elif signal_type == 'eeg_neuro':
            pattern = data.get('pattern', 'neural activity')
            count = data.get('source_count', 0)
            return f"EEG analysis: {pattern} with {count} sources [{ts_suffix}]"
        
        elif signal_type == 'environment':
            measurement = data.get('measurement', 'environmental data')
            count = data.get('source_count', 0)
            return f"Environment: {measurement} from {count} sources [{ts_suffix}]"
        
        elif signal_type == 'iot':
            device = data.get('device', source)
            gateways = data.get('gateways', data.get('devices', 0))
            return f"IoT telemetry from {device}: {gateways} active nodes [{ts_suffix}]"
        
        elif signal_type == 'cycle':
            active = data.get('active', 0)
            has_engine = data.get('has_engine', False)
            return f"Cycle status: {active} active cycles, engine={has_engine} [{ts_suffix}]"
        
        elif signal_type in ['scientific', 'statistics_europe', 'statistics_asia', 'statistics_americas']:
            count = data.get('source_count', 0)
            category = data.get('category', signal_type)
            return f"Data from {category}: {count} sources analyzed [{ts_suffix}]"
        
        else:
            category = data.get('category', signal_type)
            count = data.get('source_count', 0)
            return f"Signal from {category}: {count} data points [{ts_suffix}]"
    
    def process_signal_batch(self, signals: List[Dict]) -> int:
        """Process a batch of signals through auto-learning"""
        if not self.learner:
            logger.warning("⚠️ Auto-learner not available")
            return 0
        
        learned_count = 0
        
        for signal in signals:
            try:
                # Convert signal to question
                question = self._signal_to_question(signal)
                
                # Apply source weight
                source_type = signal.get('source_type', 'unknown')
                weight = self.config.source_weights.get(source_type, 1.0)
                
                # Learn
                result = self.learner.learn(question)
                
                if not result.get('cached', True):
                    learned_count += 1
                    self.stats['signals_learned'] += 1
                
                self.stats['last_signal_time'] = datetime.now(timezone.utc).isoformat()
                
            except Exception as e:
                logger.error(f"❌ Error processing signal: {e}")
        
        return learned_count
    
    def collect_signals_from_sources(self) -> List[Dict]:
        """Collect signals from all data sources"""
        signals = []
        
        if not self.integrator:
            return signals
        
        try:
            # Get full system overview
            overview = self.integrator.get_system_overview()
            
            # Extract data sources
            managers = overview.get('managers', {})
            data_sources = managers.get('data_sources', {})
            self.stats['sources_active'] = data_sources.get('total_sources', 0)
            
            # Create signals from each source category
            sources_by_category = data_sources.get('by_category', {})
            for category, count in sources_by_category.items():
                # Create signal for each category
                signals.append({
                    'type': category,
                    'source': f'{category}_aggregator',
                    'source_type': category,
                    'data': {
                        'category': category,
                        'source_count': count,
                        'overview': overview.get('timestamp'),
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            # Add signals from LoRa network
            lora = managers.get('lora', {})
            if lora.get('gateways', 0) > 0:
                signals.append({
                    'type': 'iot',
                    'source': 'lora_network',
                    'source_type': 'iot',
                    'data': lora,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            # Add signals from Nanogrid
            nanogrid = managers.get('nanogrid', {})
            if nanogrid.get('devices', 0) > 0:
                signals.append({
                    'type': 'iot',
                    'source': 'nanogrid_devices',
                    'source_type': 'iot',
                    'data': nanogrid,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            # Add signals from active cycles
            cycles = managers.get('cycles', {})
            if cycles.get('active', 0) > 0:
                signals.append({
                    'type': 'cycle',
                    'source': 'cycle_engine',
                    'source_type': 'system',
                    'data': cycles,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
        
        except Exception as e:
            logger.error(f"❌ Error collecting signals: {e}")
        
        return signals
    
    def run_production_loop(self, max_iterations: int = 0):
        """
        Run production learning loop
        max_iterations=0 means run forever
        """
        self.running = True
        self.stats['start_time'] = datetime.now(timezone.utc).isoformat()
        
        print("\n" + "=" * 60)
        print("🌊 KLOUD PRODUCTION AUTO-LEARNING")
        print("=" * 60)
        print(f"📡 Connected to: {self.config.hetzner_api_url}")
        print(f"📊 Signal batch size: {self.config.signal_batch_size}")
        print(f"💾 Learning batch size: {self.config.learning_batch_size}")
        print(f"🔄 Running {'forever' if max_iterations == 0 else f'{max_iterations} iterations'}...")
        print("=" * 60 + "\n")
        
        iteration = 0
        
        try:
            while self.running and (max_iterations == 0 or iteration < max_iterations):
                iteration += 1
                
                # Collect signals from sources
                signals = self.collect_signals_from_sources()
                
                # Add to buffer
                for signal in signals:
                    self.signal_buffer.push(signal)
                
                # Process batch from buffer
                batch = self.signal_buffer.pop_batch(self.config.signal_batch_size)
                learned = self.process_signal_batch(batch)
                
                # Get current stats
                buffer_stats = self.signal_buffer.stats()
                learner_stats = self.learner.get_stats() if self.learner else {}
                
                # Output status
                status_line = (
                    f"\r📊 Iter: {iteration} | "
                    f"Buffer: {buffer_stats['buffer_size']} | "
                    f"Learned: {learner_stats.get('total_learned', 0)} | "
                    f"Session: {learner_stats.get('session_learned', 0)} | "
                    f"Sources: {self.stats['sources_active']}"
                )
                sys.stdout.write(status_line + " " * 10)
                sys.stdout.flush()
                
                # Rate limiting
                time.sleep(self.config.signal_interval_sec)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping production loop...")
        
        finally:
            self.running = False
            self._cleanup()
    
    def _cleanup(self):
        """Cleanup on shutdown"""
        if self.learner:
            self.learner._async_save()
            if hasattr(self.learner, 'writer'):
                self.learner.writer.stop()
        
        print("\n✅ Production Auto-Learning stopped cleanly")
        print(f"📊 Final stats:")
        print(f"   Signals learned: {self.stats['signals_learned']}")
        print(f"   Buffer stats: {self.signal_buffer.stats()}")
        if self.learner:
            print(f"   Learner stats: {self.learner.get_stats()}")
    
    def get_health(self) -> Dict[str, Any]:
        """Health check for monitoring"""
        return {
            'status': 'healthy' if self.running else 'stopped',
            'uptime': self.stats['start_time'],
            'signals_learned': self.stats['signals_learned'],
            'sources_active': self.stats['sources_active'],
            'buffer_size': self.signal_buffer.size(),
            'last_signal': self.stats['last_signal_time'],
            'learner_available': self.learner is not None,
            'integrator_available': self.integrator is not None,
        }


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Production entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kloud Production Auto-Learning')
    parser.add_argument('--iterations', '-i', type=int, default=0, 
                        help='Max iterations (0=forever)')
    parser.add_argument('--batch-size', '-b', type=int, default=50,
                        help='Signal batch size')
    parser.add_argument('--interval', '-t', type=float, default=1.0,
                        help='Signal check interval (seconds)')
    
    args = parser.parse_args()
    
    # Create config
    config = ProductionConfig(
        signal_batch_size=args.batch_size,
        signal_interval_sec=args.interval,
    )
    
    # Run connector
    connector = ProductionAutoLearningConnector(config)
    connector.run_production_loop(max_iterations=args.iterations)


if __name__ == "__main__":
    main()

