import sys, os, logging
sys.path.insert(0, r"C:\kloud-cloud")

# Mock setup_logger
def setup_logger(name):
    return logging.getLogger(name)

# Inject into sys.modules
sys.modules['Kloud'] = type(sys)('Kloud')
sys.modules['Kloud'].colored_logger = type(sys)('colored_logger')
sys.modules['Kloud'].colored_logger.setup_logger = setup_logger

# Configure environment
os.environ['NSX_API_PORT'] = '8091'
os.environ['NSX_HB_PORT'] = '42999'
os.environ['NSX_NODE_NAME'] = 'pulse-balancer-1'

print('[LOAD BALANCER] Starting Distributed Pulse Balancer...')
with open(r'C:\kloud-cloud\distributed_pulse_balancer.py') as f:
    exec(f.read())


