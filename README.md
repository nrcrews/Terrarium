# Terrarium

A habitat of AI agents.

## Repository Setup

If you don’t have Python installed, [download it here](https://www.python.org/downloads/).

1. Clone this repository.

2. Navigate to the project directory:

```bash
cd Terrarium
```

3. Create a new virtual environment:

```bash
virtualenv virt
source virt/bin/activate
```

4. Install the requirements:

```bash
pip install -r requirements/cli.txt
```

5. Make a copy of the example environment variables file

```bash
cp .env.example .env
```

6. Populate the .env file variables.

## CLI Execution

1. Run the application

```bash
./cli.sh
```

## Available Tools

You can pick and choose what tools your agent has access to.

### Local

* `get_current_date_time`
* `delete_file`
* `list_files`
* `move_file`
* `read_file`
* `write_file`

### Remote

**Coming soon!**

## Contributing

All contributions are welcome! Reach out for more information.
