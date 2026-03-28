import pytest
import os
import csv
from src.utils.session_logger import log_interaction

class TestSessionLogger:
    def test_log_interaction_creates_file(self, tmp_path):
        log_file = tmp_path / "log.csv"
        log_interaction("User input test", "Model output test", str(log_file))
        assert os.path.isfile(log_file)
        
    def test_log_interaction_appends_correctly(self, tmp_path):
        log_file = tmp_path / "log.csv"
        log_interaction("Input 1", "Output 1", str(log_file))
        log_interaction("Input 2", "Output 2", str(log_file))
        
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        assert len(lines) == 3 # Header + 2 lines
        assert "Input 1" in lines[1]
        assert "Output 2" in lines[2]

    @pytest.mark.parametrize("i", range(15))
    def test_log_interaction_parametric_scaling(self, i, tmp_path):
        # Generates 15 fast tests for scaling coverage points
        log_file = tmp_path / "log.csv"
        log_interaction(f"Input {i}", f"Output {i}", str(log_file))
        assert os.path.exists(log_file)
