import requests
from VARIABLES import*
import tqdm

#this is a sample client script to test FLASK API endpoints

base_url = api_url_endpoint

def list_models():
    url = f'{base_url}/list'  # Update this URL if your server is running on a different host/port
    try:
        response_from_url = requests.post(url)
        
        if response_from_url.status_code == 200:
            data_from_client = response_from_url.json()
            return data_from_client.get('models', {})
        else:
            print(f"Failed to get models list. Status code: {response_from_url.status_code}")
            return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}
    
# if __name__ == "__main__":
#     models = list_models()
#     print("Available models and sizes in GB:", models)


def generate_embeddings_client(text, model_name):
    url = f'{base_url}/generate_embeddings'  

    # Prepare JSON data
    data_to_url = {
        'text': text,
        'modelname': model_name
    }

    # Send POST request
    response = requests.post(url, json=data_to_url)

    # Check response status code
    if response.status_code == 200:
        result = response.json()
        if 'embeddings' in result:
            return result['embeddings']
        elif 'error' in result:
            return f"Error: {result['error']}"
        else:
            return "Unknown error occurred."
    else:
        return f"Error: Request failed with status code {response.status_code}."

# # Example usage
# if __name__ == "__main__":
#     text = "this is for you"
#     model_name = "mxbai-embed-large-v1"

#     result = generate_embeddings_client(text, model_name)
#     print(result)


def download_model(model_name):
    url = f'{base_url}/pull'  
    data = {
        'name': model_name
    }
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            print("Success:", response_data['response'])
        elif response.status_code == 400:
            print("Error:", response_data['error'])
        elif response.status_code == 500:
            print("Error:", response_data['error'])
        else:
            print("Unexpected status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)

# if __name__ == '__main__':
#     model_name = input("Enter the model name: ")
#     download_model(model_name)

def delete_model(file_name):
    """
    Sends a POST request to the Flask route to delete a model.

    Args:
    file_name (str): The name of the model file to be deleted.

    Returns:
    dict: The JSON response from the server.
    """
    url = f'{base_url}/delete_model'
    headers = {'Content-Type': 'application/json'}
    data = {'model_name': file_name}

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print(f"Success: {response.json()['message']}")
    elif response.status_code == 404:
        print(f"Error: {response.json()['error']}")
    else:
        print(f"Unexpected status code {response.status_code}: {response.text}")

    return response.json()

# Example usage
# file_to_delete = 'mxbai-embed-large-v1-f16'
# delete_model(file_to_delete)


import requests
import json

## below code is for streaming response

def chat_client_s(prompt_list, model_name,stream_s):
    url = f'{base_url}/generate'  

    # Prepare JSON data
    data_to_url = {
        'prompt_lst': prompt_list,
        'modelname': model_name,
        'stream': stream_s  
    }

    # Send POST request with stream=True
    with requests.post(url, json=data_to_url, stream=True) as response:
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if 'chunk' in chunk:
                        yield chunk['chunk']
                    elif 'error' in chunk:
                        yield f"Error: {chunk['error']}"
        else:
            yield f"Error: Request failed with status code {response.status_code}."

# Example usage
# if __name__ == "__main__":
#     while True :
#         user = input("enter the query: ")
#         if user == 'q':
#             break
#         else:
#             list_of_prompt = [
#                 {"role": "system", "content": "You are a friendly assistant. Always talk in tone of a pirate."},
#                 {"role": "user", "content": user}
#             ]
#             model_name = "gemma-2b-it-q4_k_m.gguf"

#             print("Streaming response:")
#             for chunk in chat_client_s(list_of_prompt, model_name,stream_s=True):
#                 print(chunk, end='', flush=True)
#             print()  # Print a newline at the end

def chat_client_ns(prompt_list, model_name):
    url = f'{base_url}/generate'  

    # Prepare JSON data
    data_to_url = {
        'prompt_lst': prompt_list,
        'modelname': model_name,
        'stream': False  # Set to False for non-streaming
    }

    # Send POST request
    response = requests.post(url, json=data_to_url)

    # Check response status code
    if response.status_code == 200:
        result = response.json()
        if 'response' in result:
            return result['response']
        elif 'error' in result:
            return f"Error: {result['error']}"
        else:
            return "Unknown error occurred."
    else:
        return f"Error: Request failed with status code {response.status_code}."

# Example usage
# if __name__ == "__main__":
#     list_of_prompt = [
#         {"role": "system", "content": "You are a geography assistant. You have to give answers related to geography subject only."},
#         {"role": "system", "content": "Your name is 'Capybara'."},
#         {"role": "user", "content": "Introduce yourself."},
#         {"role": "assistant", "content": "Hi! My name is Capybara, your geography assistant."},
#         {"role": "user", "content": "Introduce yourself."}
#     ]
#     model_name = "gemma-2b-it-q4_k_m.gguf"

#     res = chat_client_ns(list_of_prompt, model_name)
#     print("Non-streaming response:", res)

def download_model_p(model_name):
    url = f'{base_url}/pull_c'
    data = {
        'name': model_name
    }
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        with requests.post(url, json=data, headers=headers, stream=True) as response:
            response.raise_for_status()  

            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kilobyte

            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
            data = b''
            for chunk in response.iter_content(block_size):
                if chunk:
                    data += chunk
                    progress_bar.update(len(chunk))
            progress_bar.close()

            response_data = response.json()
            if response.status_code == 200:
                print("Success:", response_data['response'])
            elif response.status_code == 400:
                print("Error:", response_data['error'])
            elif response.status_code == 500:
                print("Error:", response_data['error'])
            else:
                print("Unexpected status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)

if __name__ == '__main__':
    model_name = input("Enter the model name: ")
    download_model_p(model_name)