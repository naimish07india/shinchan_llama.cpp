import os

current_working_dir_path=os.getcwd() #get current working directory path

model_dir_path=f"{current_working_dir_path}\MODELS" #path of directory where models are present

json_path=f"{current_working_dir_path}\model_name_urls.json" #path of json file with urls and model name

api_url_endpoint = "http://127.0.0.1:5000"
# print(model_dir_path)