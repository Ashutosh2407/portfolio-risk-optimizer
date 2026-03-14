
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.models.optimizer import PortfolioOptimizer
#from ...src.models.optimizer import PortfolioOptimizer

def get_optimizer():
    return PortfolioOptimizer()
