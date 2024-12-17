# PROJECT Shinchan

The main objective of this project is to run LLM models on local machine using "llama.cpp" and provide endpoints for required features.

## Installation

Install dependencies by executing following command:

"pip install -r requirements.txt"

## USAGE

This project contains "MODELS" folder that contains all available model's GGUF file.

### funcs.py 
This file contains all the required functions for this project:

F1: find_model() -- this function takes model name and look for it in MODELS folder and returns it's path.

F2: list_models() -- this function returns the list of all available models.

F3: generate_embeddings() -- this function takes text and modelname and returns embeddings to the input text.

F4: generate_response() -- this function take suser query and model name and returns response generated from LLM.

### server.py

This file contains all available routes:

"/list" -- use this route to know all available models, Takes no input.

"/generate" -- use this route to generate response from LLM.

"/generate_embeddings" -- use this route to generate embeddings.

## CODE TO USE IN PYHTON SCRIPT

### To create embeddings :
```
url='your_url/generate_embeddings'

data = {
        'prompt_lst': text,
        'modelname': model_name ## model of your choice
       }

    # Send POST request
response = requests.post(url, json=data)

result = rsponse.json()

print(result['embeddings'])

```

### To generate response/chat :
```
url='your_url/generate'
messages=[
             {"role": "system", "content": "You are a geography assistant. Your have to give answers related to geography subject only."},
             {"role": "system", "content": "Your name is 'Shinchan'."},
             {"role": "user", "content": "Introduce yourself."},
             {"role": "assistant", "content": "Hi! My name is Shinchan, your geography assistant."},
             {"role": "user", "content": "Inroduce yourself."}
         ]
data = {
        'prompt_lst': messages,
        'modelname': model_name ## model of your choice
        'stream': False ## true for streaming
       }

    # Send POST request
response = requests.post(url, json=data)

result = rsponse.json()

print(result['response'])

```

### To get list of available models
```
url = 'your_url/list'

response = requests.post(url)

data = response.json()

print(data.get('models', []))

```

### To pull model from huggingface
```
url = 'your_url/pull'

data = {
        'name': "name of the model" ## model of your choice
       }

response = requests.post(url, json = data)

data = response.json()

print(data)

```
### To delete model
```
url = 'your_url/delete'

data = {
        'model-name': "name of the model" ## model of your choice
       }

response = requests.post(url, json = data)

data = response.json()

print(data)

```

# CLI commands

This section describe the available command-line interface (CLI) commands for shinchan.

## Available Commands

### shinchan list

List all the available models along with their size in GB.
eg. shinchan list

### shinchan run 'modelname'

Loads the mentioned model to generate response to user queries.
eg. shinchan run gemma-2b-it-q4_k_m.gguf

### shinchan delete 'modelname' 

Deletes the mentioned model.
eg. shinchan delete gemma-2b-it-q4_k_m.gguf

### shinchan generate-embeddings "text-to-generate-embeddings-for" "model-to-generate-embeddings-for"

Returns list of embeddings for the given text
eg. shinchan generate-embeddings "text for embeddings" "mxbai-embed-large-v1-f16"

### shinchan pull 'modelname' 

Downloads the given model in your local machine
eg. shinachan pull gemma-2b-it-q4_k_m.gguf

### shinchan --help 

This command helps you to show all the available commands.
eg. shinchan --help
OUTPUT:
Usage: shinchan [OPTIONS] COMMAND [ARGS]...

  A simple CLI tool to interact with the Flask API.

Options:
  --help  Show this message and exit.

Commands:
  delete               Delete a model by its name.
  generate-embeddings  Generate embeddings for the given text using the...
  list                 List all available models.
  pull                 Pull a model by its name.
  run                  Start an interactive session with the model.

Shinchan id Created by Naimish Pal. For any info call him.


