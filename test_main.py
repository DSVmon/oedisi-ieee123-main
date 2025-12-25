import unittest
from unittest.mock import patch, MagicMock
import sys
import io
import config
import main

class TestMain(unittest.TestCase):
    def setUp(self):
        # Save original language to restore after tests
        self.original_language = config.LANGUAGE

    def tearDown(self):
        config.LANGUAGE = self.original_language

    @patch('main.plot_interactive_topology')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_success_ru(self, mock_stdout, mock_plot):
        """Test main execution in Russian (default) without errors."""
        config.LANGUAGE = 'RU'
        main.main()

        output = mock_stdout.getvalue()

        # Verify plot function was called
        mock_plot.assert_called_once()

        # Verify output contains Russian text
        self.assertIn("=== OpenDSS IEEE 123 Запуск Симуляции ===", output)
        self.assertIn("1. Запуск интерактивной топологии...", output)
        self.assertIn("2. Кликайте на узлы на графике для расчета режимов.", output)

    @patch('main.plot_interactive_topology')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_success_en(self, mock_stdout, mock_plot):
        """Test main execution in English."""
        config.LANGUAGE = 'EN'
        main.main()

        output = mock_stdout.getvalue()

        # Verify output contains English text
        self.assertIn("=== OpenDSS IEEE 123 Simulation Launcher ===", output)
        self.assertIn("1. Launch interactive topology...", output)
        self.assertIn("2. Click nodes on the plot to calculate regimes.", output)

    @patch('builtins.input', return_value='') # Mock input to avoid waiting
    @patch('main.plot_interactive_topology')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_main_exception(self, mock_stdout, mock_plot, mock_input):
        """Test main exception handling."""
        config.LANGUAGE = 'RU'
        # Simulate an error in the topology plotter
        mock_plot.side_effect = Exception("Test Error")

        main.main()

        output = mock_stdout.getvalue()

        # Verify error message is printed
        self.assertIn("Критическая ошибка: Test Error", output)
        # Verify input was called (Press Enter to exit...)
        mock_input.assert_called_once()

if __name__ == '__main__':
    unittest.main()
