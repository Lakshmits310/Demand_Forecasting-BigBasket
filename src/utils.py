import os

def get_data_path(relative_path: str) -> str:
    """Absolute path for files inside data/processed"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "data", "processed", relative_path)
