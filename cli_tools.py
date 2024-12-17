import click
import requests
import logging
from logging.handlers import RotatingFileHandler
from VARIABLES import *
import json
import sys
from tqdm import tqdm

BASE_URL = api_url_endpoint

logger = logging.getLogger('cli_tool')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('cli_tool.log', maxBytes=10000, backupCount=1) 
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class CustomGroup(click.Group):
    def format_help(self, ctx, formatter):
        
        super().format_help(ctx, formatter)
        # Adding custom footer for the --help command 
        formatter.write_paragraph()
        formatter.write_text("Shinchan is Created by Naimish Pal. For any info contact him at naimishindia2003@gmail.com.")



@click.group(cls=CustomGroup)
#this creates a simple header for the --help command
def cli():
    """A simple CLI tool to interact with the Flask API."""
    pass


@cli.command()
def list():
    """List all available models."""
    url = f'{BASE_URL}/list'
    logger.info(f'Sending POST request to {url}')
    try:
        response = requests.post(url)
        
        if response.status_code == 200:
            models = response.json().get('models', {})
            logger.info(f'Received response: {models}')

            if not models:
                click.echo("No models available.")
                return

            # Calculating the maximum length of model names for formatting
            max_name_length = max(len(name) for name in models.keys())
            
            # Printing header
            click.echo(f'{"Name":<{max_name_length}}         Size')
            click.echo(f'{"-"*max_name_length}        ------')
            
            # Printing each model name and size
            for name, size in models.items():
                click.echo(f'{name:<{max_name_length}}        {size:>5}')
        else:
            # Displaying server error message
            error_msg = response.json().get('error', 'Unknown error')
            logger.error(f'Error in response: {error_msg}')
            click.echo(f"Error: {error_msg}")

    except requests.ConnectionError:
        error_msg = "Unable to connect to the server. Please ensure that the server is running."
        logger.error(error_msg)
        click.echo(f"Error: {error_msg}")
        
    except requests.RequestException as e:
        logger.error(f'Request failed: {str(e)}')
        click.echo(f"Request failed: {str(e)}")




@cli.command()
@click.argument('text')
@click.argument('modelname')
def generate_embeddings(text, modelname):
    """Generate embeddings for the given text using the specified model."""
    url = f'{BASE_URL}/generate_embeddings'
    payload = {'text': text, 'modelname': modelname}
    
    logger.info(f'Generating embeddings using model: {modelname}')
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  
        
        data = response.json()
        if 'error' in data:
            raise ValueError(data['error'])
        
        embeddings = data.get('embeddings')
        if not embeddings:
            logger.warning('Received empty embeddings')
            click.echo("Warning: Received empty embeddings")
        else:
            click.echo('Embeddings generated successfully')
            click.echo(f'Embeddings: {embeddings}')
        
        logger.info(f'Embeddings generated for model {modelname}: {embeddings}')

    except requests.ConnectionError:
        error_msg = "Unable to connect to the server. Please ensure that the server is running."
        logger.error(error_msg)
        click.echo(f"Error: {error_msg}")
    
    except (requests.RequestException, ValueError) as e:
        error_msg = f"Error: {str(e)}"
        click.echo(error_msg)
        logger.error(error_msg)



@cli.command()
@click.argument('name')
def pull(name):
    """Pull a model by its name."""
    url = f'{BASE_URL}/pull_cli'
    payload = {'name': name}
    
    logger.info(f'Initiating pull for model: {name}')
    click.echo(f'Initiating model pull: {name}')
    
    try:
        with requests.post(url, json=payload, stream=True) as response:
            response.raise_for_status() 

            # Checking if the response contains JSON error message
            if 'application/json' in response.headers.get('Content-Type', ''):
                result = response.json()
                if 'error' in result:
                    error_msg = result['error']
                    click.echo(f"Error: {error_msg}")
                    logger.error(f"Error pulling model {name}: {error_msg}")
                    return

            # Otherwise, handling the file streaming
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kilobyte
            
            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
            data = b''
            for chunk in response.iter_content(block_size):
                data += chunk
                progress_bar.update(len(chunk))
            progress_bar.close()
            
            click.echo("Model download complete.")
            logger.info(f"Model {name} pulled successfully.")
    except requests.ConnectionError:
        error_msg = "Unable to connect to the server. Please ensure that the server is running."
        logger.error(error_msg)
        click.echo(f"Error: {error_msg}")
    except requests.RequestException as e:
        error_msg = f"HTTP error occurred: {str(e)}"
        click.echo(f"Error: {error_msg}")
        logger.error(error_msg)
    except ValueError as e:
        error_msg = f"Value error: {str(e)}"
        click.echo(f"Error: {error_msg}")
        logger.error(error_msg)



@cli.command()
@click.argument('model_name')
def delete(model_name):
    """Delete a model by its name."""
    url = f'{BASE_URL}/delete'
    payload = {'model_name': model_name}
    
    logger.info(f'Initiating deletion for model: {model_name}')
    click.echo(f'Initiating model deletion: {model_name}')
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', 'Model deleted successfully')
            click.echo(message)
            logger.info(f'Model {model_name} deleted successfully: {message}')
        else:
            error_msg = response.json().get('error', 'Unknown error occurred')
            click.echo(f"Error: {error_msg}")
            logger.error(f"Error deleting model {model_name}: {error_msg}")
    
    except requests.ConnectionError:
        error_msg = "Unable to connect to the server. Please ensure that the server is running."
        logger.error(error_msg)
        click.echo(f"Error: {error_msg}")
    
    except requests.RequestException as e:
        error_msg = f"Error occurred while deleting model: {str(e)}"
        click.echo(f"Error: {error_msg}")
        logger.error(f"Error deleting model {model_name}: {str(e)}")



@cli.command()
@click.argument('modelname')
def run(modelname):
    """Start an interactive session with the model."""
    click.echo("Send a message. Type '/bye' to exit.")

    while True:
        query = click.prompt('>>>', prompt_suffix="")
        if query.strip().lower() == '/bye':
            click.echo("Session Ended")
            break

        try:
            url = f'{BASE_URL}/run'
            payload = {'prompt': query, 'modelname': modelname}
            with requests.post(url, json=payload, stream=True) as response:
                if response.status_code == 200:
                    sys.stdout.write("AI: ") 
                    sys.stdout.flush()
                    first_chunk = True
                    for line in response.iter_lines(decode_unicode=True):
                        if line:
                            try:
                                data = json.loads(line)
                                if 'chunk' in data:
                                    chunk = data['chunk']
                                    if first_chunk:
                                        sys.stdout.write(chunk.lstrip())  
                                        first_chunk = False
                                    else:
                                        sys.stdout.write(chunk)
                                    sys.stdout.flush()
                                elif 'error' in data:
                                    click.echo(f"\nError: {data['error']}")
                                    logger.error(f"Error from server: {data['error']}")
                            except json.JSONDecodeError:
                                click.echo(f"\nError decoding JSON: {line}")
                                logger.error(f"Error decoding JSON: {line}")
                    click.echo("")
                else:
                    error_data = response.json()
                    error_message = error_data.get('error', 'Unknown error occurred')
                    click.echo(f"\nError: {error_message}")
                    logger.error(f"Error from server: {error_message}")

        except requests.ConnectionError:
            error_msg = "Unable to connect to the server. Please ensure that the server is running."
            logger.error(error_msg)
            click.echo(f"Error: {error_msg}")

        except requests.RequestException as e:
            click.echo(f"\nRequest failed: {str(e)}")
            logger.error(f"Request failed: {str(e)}")


if __name__ == '__main__':
    logger.info('Starting CLI tool')
    cli()
    logger.info('CLI tool finished')
