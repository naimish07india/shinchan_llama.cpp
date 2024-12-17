import os
from llama_cpp import Llama
import json
import requests
from VARIABLES import*
from flask import Response, jsonify

model_dir_path = model_dir_path
json_path = json_path

with open(json_path) as file:
    model_url_dict=json.load(file)  # loading json file in "url_dict"


# Necessary function
def find_model(file_name):
    """ Returns file path of model.
    Args: file_name(str): name of the model user is asking.
    Output: returns file_path or error.
    """
    
    folder_path=model_dir_path
    
    for root, dirs, files in os.walk(folder_path):
        if file_name in files:
            return os.path.join(root, file_name)
    
    return f"Error: No such model, try pulling '{file_name}'."


# Stream response from llm in streaming format
def response_stream(llm, prompt_lst):
    """ generates responses from llm in streaming.
    Args: llm (llm instance)
          prompt_lst(lst): list of prompts
    Output: streamed response
    """

    for chunk in llm.create_chat_completion(messages=prompt_lst, stream=True):
        if 'choices' in chunk and len(chunk['choices']) > 0:
            content = chunk['choices'][0].get('delta', {}).get('content', '')
            if content:
                yield content


# Repsonse from llm as a whole response
def response_non_stream(llm, prompt_lst):
    """ Generates response as a complete string.
    Args: llm(llm instance)
          prompt_lst(lst): list of prompts
    Output: response from llm in string format
          """

    data_from_llm = llm.create_chat_completion(
        messages=prompt_lst,
        stream=False
    )
    return data_from_llm['choices'][0]['message']['content']


# LIST API
def list_models():
    """ Returns a dictionary of available models with their sizes in gigabytes. """

    models_dict = {}
    
    try:
        
        files = os.listdir(model_dir_path)
        
        for file_name in files:
            file_path = os.path.join(model_dir_path, file_name)
            
           
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)  
                file_size_gb = file_size / (1024 ** 3)  
                models_dict[file_name] = f"{file_size_gb:.2f}"
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return models_dict


# Generating Embeddings API
def generate_embeddings(text,model_name):
    """Generate embeddings from a text.
    Args: text(str): text to generate embeddings for 
          model_name(str): name of the model
    Output: returns list of embeddings
    """

    model_path = find_model(model_name)
    
    if "Error" in model_path:
        return model_path  # Return the error message
    
    llm = Llama(model_path=model_path, embedding=True, verbose=False)
    
    output = llm.create_embedding(text)
    embeddings_lst = []

    for entry in output['data']:
        if entry.get('object') == 'embedding':
            embeddings_lst.append(entry['embedding']) ##Extracting only embeddings

    return embeddings_lst


# Genrating response API
def generate_response(prompt_lst, model_name, stream):
    """Returns response from llm
    Args: prompt_lst(lst): list of prompts
          model_name(str): name of model to use
          stream(bol): True for response streaming else False
    Output: If stream =True then, Generator yielding chunks of response
            If stream =False then, string of response
    """

    model_path = find_model(model_name)
    
    if "Error" in model_path:
        return model_path  # Return the error message
    
    llm = Llama(
        model_path=model_path,
        verbose=False
    )
    
    if stream:
        return response_stream(llm, prompt_lst)
    else:
        return response_non_stream(llm, prompt_lst)
    

# Run Generation response API for CLI
def generate_response_run_cli(user_prompt, model_name):
    """Returns response from llm
    Args: user_prompt(str): query from user
          model_name(str): name of model to use
    Output: Generator yielding chunks of response   
    """

    model_path = find_model(model_name)
    
    if "Error" in model_path:
        return model_path  # Return the error message
    
    llm = Llama(
        model_path=model_path,
        verbose=False
    )
    prompt_lst = [
         {"role": "system", "content": "You are a large languag model trained to answer smartly to user's questions in an interactive manner."},
         {"role": "user", "content": user_prompt}
    ]
    
    return response_stream(llm, prompt_lst)


# Model Pull API
def pull_model(name):
    """Download model given its name using the JSON file structure."""
    model_info = model_url_dict.get(name)
    
    if model_info is None:
        return f"No information found for model: {name}"
    
    url_for_model_download = model_info.get('url')
    
    if url_for_model_download is None:
        return f"No URL found for model: {name}"
    
    save_dir = model_dir_path
    os.makedirs(save_dir, exist_ok=True)
    
    model_filename = os.path.join(save_dir, f"{name}")
    
    # Check if the file already exists
    if os.path.isfile(model_filename):
        return f"File '{name}' already exists."
    
    try:
        response = requests.get(url_for_model_download)
        response.raise_for_status()  # Check if the request was successful
        
        with open(model_filename, 'wb') as file:
            file.write(response.content)
        
        return f"Model downloaded"
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"


# Model Delete API
def delete_model(file_name):
    """
    Deletes model with the given name.

    Args:
    file_name (str): The name of the file to be deleted.

    Returns:
    bool: True if the file was successfully deleted, False otherwise.
    """
    directory_path = model_dir_path
    # Construct the full path to the file
    model_path = os.path.join(directory_path, file_name)
    
    try:
        # Check if the file exists
        if os.path.isfile(model_path):
            # Delete the file
            os.remove(model_path)
            print(f"Model '{file_name}' successfully deleted.")
            return True
        else:
            print(f"Model '{file_name}' not found.")
            return False
    except Exception as e:
        print(f"An error occurred while trying to delete the file: {e}")
        return False
    

## Download model with progress bar in CLI
def download_model_cli(name):
    """Download model given its name using the JSON file structure."""
    model_info = model_url_dict.get(name)

    save_dir = model_dir_path
    os.makedirs(save_dir, exist_ok=True)
    
    model_filename = os.path.join(save_dir, f"{name}")
    
    # Check if the file already exists
    if os.path.isfile(model_filename):
        return jsonify({"error": f"File '{name}' already exists."}), 200
    
    if model_info is None:
        return jsonify({"error": f"No information found for model: {name}"}), 404
    
    url_for_model_download = model_info.get('url')
    
    if url_for_model_download is None:
        return jsonify({"error": f"No URL found for model: {name}"}), 404
    
    
    try:
        response = requests.get(url_for_model_download, stream=True)
        response.raise_for_status()  # Check if the request was successful
        
        def generate():
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk
        
        # Headers for file download
        headers = {
            'Content-Disposition': f'attachment; filename={name}',
            'Content-Type': 'application/octet-stream'
        }
        
        return Response(generate(), headers=headers), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500