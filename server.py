'''
APIs:

1. LIST: list the available models
route: /list
input: nil
output: table of available models in the MODEL directory

2. EMBEDDINGS: generate embeddings 
route: /generate_embeddings
input: text
output: embeddings

3. GENERATE: generate response to the user's query
route: /generate
input: {  
    "messages": "list of messages in required format:
                ["system": "<system prompt here>",
                "assistant": "<assistant prompt here>",
                "user": "<user prompt here>"]"
    "model": "model name present in the MODELS directory (models can be listed using the list api route)"
    }
output: response

4. PULL: pull models from huggingface
route: /pull
input: {
"model_name":'name of the model'
}


JSON Formats:
input JSON format (client payload):
{   
    "prompt": "<user prompt/query here>",
    "model": "model name present in the MODELS directory (models can be listed using the list api route)"
}

    
output JSON format (server response):
{
    "response": "<response here>"
}

'''

# Library Imports
from flask import Flask, jsonify, request, Response,stream_with_context
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import json

# Utility Imports
from funcs import list_models, generate_embeddings, generate_response, pull_model, delete_model, generate_response_run_cli, download_model_cli
# setting up the server
app = Flask(__name__)
CORS(app)  # enable CORS

# Configure logging
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)  # Rotate log file
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


# LIST API 
@app.route('/list', methods=['POST'])
def list_models_route():
    try:
        # Call the list_models function without arguments
        models_dict = list_models()
        app.logger.info('List models request successful')
        return jsonify({'models': models_dict})
    except Exception as e:
        app.logger.error(f'Error listing models: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500



# Embeddings API 
@app.route('/generate_embeddings', methods=['POST'])
def generate_embeddings_route():
    try:
        data = request.json
        if 'text' not in data or 'modelname' not in data:
            return jsonify({'error': 'Required fields "text" and "modelname" not provided.'}), 400

        text = data['text']
        model_name = data['modelname']

        embeddings = generate_embeddings(text, model_name)

        if "Error" in embeddings:
            app.logger.error(f'Error generating embeddings: {embeddings}')
            return jsonify({'error': embeddings})
        else:
            app.logger.info('Embeddings generated successfully')
            return jsonify({'embeddings': embeddings})
    except Exception as e:
        app.logger.error(f'Error generating embeddings: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500



# Pull model API 
@app.route('/pull', methods=['POST'])
def pull():
    try:
        data = request.get_json()
        if 'name' not in data:
            return jsonify({"error": "Model name is required"}), 400

        name = data['name']

        resp = pull_model(name)

        if "Error" in resp:
            app.logger.error(f'Error pulling model: {resp}')
            return jsonify({'error': resp})
        else:
            app.logger.info(f'Model pulled successfully: {name}')
            return jsonify({'response': resp})
    except Exception as e:
        app.logger.error(f'Error pulling model: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500



# Delete model API 
@app.route('/delete', methods=['POST'])
def delete_model_route():
    try:
        data = request.get_json()
        file_name = data.get('model_name')

        if not file_name:
            return jsonify({"error": "model_name is required"}), 400

        if delete_model(file_name):
            app.logger.info(f"Model '{file_name}' successfully deleted")
            return jsonify({"message": f"Model '{file_name}' successfully deleted"}), 200
        else:
            app.logger.error(f"Model '{file_name}' not found ")
            return jsonify({"error": f"Model '{file_name}' not found "}), 404
    except Exception as e:
        app.logger.error(f'Error deleting model: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500



# Response API
@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        if 'prompt_lst' not in data or 'modelname' not in data:
            return jsonify({'error': 'Required fields "prompt_lst" and "modelname" not provided.'}), 400

        prompt_lst = data['prompt_lst']
        model_name = data['modelname']
        stream = data.get('stream')  # Default to False if not provided

        response = generate_response(prompt_lst, model_name, stream)

        if isinstance(response, str) and response.startswith("Error"):
            app.logger.error(f'Error generating response: {response}')
            return jsonify({'error': response}), 400
        
        if stream:
            def generate():
                try:
                    for chunk in response:
                        yield json.dumps({'chunk': chunk}) + '\n'
                except Exception as e:
                    app.logger.error(f'Error in streaming response: {str(e)}')
                    yield json.dumps({'error': 'Error in streaming response'})

            return Response(stream_with_context(generate()), content_type='application/json')
        else:
            app.logger.info('Response generated successfully')
            return jsonify({'response': response})

    except Exception as e:
        app.logger.error(f'Error generating response: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500



#Response API for CLI 
@app.route('/run', methods=['POST'])
def generate_run():
    try:
        data = request.json
        if 'prompt' not in data or 'modelname' not in data:
            return jsonify({'error': 'Required fields "prompt" and "modelname" not provided.'}), 400

        user_prompt = data['prompt']
        model_name = data['modelname']

        response = generate_response_run_cli(user_prompt, model_name)

        if isinstance(response, str) and response.startswith("Error"):
            app.logger.error(f'Error generating response: {response}')
            return jsonify({'error': response}), 400

        def generate():
            try:
                for chunk in response:
                    yield json.dumps({'chunk': chunk}) + '\n'
            except Exception as e:
                app.logger.error(f'Error in streaming response: {str(e)}')
                yield json.dumps({'error': 'Error in streaming response'})

        return Response(stream_with_context(generate()), content_type='application/json')

    except Exception as e:
        app.logger.error(f'Error generating response: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


# for cli
@app.route('/pull_cli', methods=['POST'])
def pull_cli():
    try:
        data = request.get_json()
        if 'name' not in data:
            return jsonify({"error": "Model name is required"}), 400

        name = data['name']

        resp, status_code = download_model_cli(name)

        if isinstance(resp, Response):
            app.logger.info(f'Response from: {name}')
            return resp
        else:
            app.logger.error(f'Error pulling model: {resp.get_json().get("error")}')
            return resp, status_code
    except Exception as e:
        app.logger.error(f'Error pulling model: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
