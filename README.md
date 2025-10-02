# Video Stutter Detector

This project is designed to detect stuttering in video playback using Python. It provides a comprehensive set of tools for analyzing video performance and identifying issues related to stuttering.

## Project Structure

- **.gitignore**: Specifies files and directories that should not be tracked by Git.
- **.vscode/settings.json**: Contains project settings for Visual Studio Code.
- **notebooks/02_dpframe_test_ver.0.0.1.ipynb**: A Jupyter notebook for experiments and analysis related to video stutter detection.
- **src/detector/**: Contains the core functionality for detecting video stuttering.
  - **__init__.py**: Initializes the detector package.
  - **main.py**: Entry point for the application, starting the video stutter detection process.
  - **processor.py**: Defines functions and classes for processing video data.
  - **analyzer.py**: Contains logic for analyzing video stuttering.
  - **utils.py**: Provides auxiliary functions and utilities.
  - **cli.py**: Offers a command-line interface for running the program.
- **src/tests/**: Contains unit tests for the detector module.
  - **test_processor.py**: Unit tests for processor.py.
  - **test_analyzer.py**: Unit tests for analyzer.py.
- **tests/integration_test.py**: Script for running integration tests.
- **scripts/run_detection.sh**: Shell script containing commands to execute the video stutter detection process.
- **requirements.txt**: Lists the Python packages required for the project.
- **pyproject.toml**: Manages project metadata and dependencies.
- **setup.cfg**: Contains project settings and options.

## Installation

To install the required packages, run:

```
pip install -r requirements.txt
```

## Usage

To run the video stutter detection process, use the command line interface provided in `cli.py` or execute the shell script `run_detection.sh`.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.