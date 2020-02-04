# Blockchain 101

Simple blockchain written in python

## Installation

1. Make sure [Python 3.6+](https://www.python.org/downloads/) is installed.
2. Install [poetry](https://github.com/sdispater/poetry).
3. Install requirements
```
$ poetry install
```

4. Copy `.env.example` to `.env`

5. Start some nodes:
	* `$ poetry run flask run -p 5000`
	* `$ poetry run flask run -p 5001`

## Docker

Another option for running this blockchain program is to use Docker.  Follow the instructions below to create a local Docker container:

1. Build the docker image

```
$ docker-compose build
```

2. Run the nodes

```
$ docker-compose up -d
```

4. To add more nodes, add a new service to the `docker-compose.yml` file
and adjust the port number.

```yaml
node2:
	build: .
	ports:
		- 5002:80
```

## Credits

[dvf](github.com/dvf/) for the original blockchain code
