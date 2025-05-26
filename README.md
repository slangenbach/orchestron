# Orchestron

The tiny ML Pipeline orchestrator

## Prerequisites

- [uv][1]
- [Task][2]

## Installation

1. Make sure you meet the prerequisites
1. Setup the development environment: `task setup`

## Configuration

Edit the **.env** file in project root directory and set the following variables:

| Variable | Description | Note |
| --- | --- | --- |
| LOG_LEVEL | Set the logging level | Defaults to 'INFO'

## Usage

1. Start the API locally: `task dev:start-api`
1. Check out the [docs](http://127.0.0.1:8000/docs) for available endpoints

## Contributing

1. Create a dedicated branch
1. Add your contribution
1. Run linters: `task lint`
1. Run tests: `task test`
1. Commit, push and create a merge request


[1]: https://docs.astral.sh/uv/
[2]: https://taskfile.dev/
