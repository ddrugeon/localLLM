# LocalLLM

LocalLLM is a toy project to experiment SLM and LLM in python. Its
main goal is to help me to launch a multimedia file located in my NAS
by using a local LLM.

## Getting Started

### Prerequisites

- Python >=3.12.0 <3.13.0 (tested with 3.12.5)
- uv >=0.4.30 (tested with 0.4.30)
- pre-commit >=3.2.0 <4.0.0 (tested with 3.6.0)
- go-task >=3.0.0
- ollama >=0.4.0
- docker (optional)

### Installation

1. Clone the repository: `git clone https://github.com/your-username/your-repo-name.git`
2. Install dependencies: `uv install`
3. Set up pre-commit hooks: `pre-commit install`

### Testing

Run tests using the `test` task: `task test`

### Docker

Build and run the Docker container using the `docker` task: `task docker`

## Project Structure

- `src/`: Source code for the project
- `data/inputs/`: Input data for the project
- `Taskfile.yml`: Task definitions for the project

## Running the project

Run the project using the `run` task: `task run`

## Contributing

Contributions are welcome! Please submit a pull request with your changes.

## References

- [Python boilerplate with pre-commit, uv, and Docker](https://github.com/smarlhens/python-boilerplate)
