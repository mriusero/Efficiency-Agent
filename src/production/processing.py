from .metrics.tools import tools_metrics
from .metrics.machine import machine_metrics

def process(raw_data):
    """
    Process the raw production data to extract metrics.
    """
    tools_metrics(raw_data)
    machine_metrics(raw_data)
