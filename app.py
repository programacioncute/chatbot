import os
import ast
import time
import requests
import logging
import numpy as np
import openai
import pandas as pd
import tiktoken
import openai
import asyncio
import threading
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file, abort
import concurrent.futures
import locale

# from timeout_decorator import timeout

import concurrent.futures
from sklearn.metrics.pairwise import cosine_similarity

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
# from approaches.retrievethenread import RetrieveThenReadApproach
# from approaches.readretrieveread import ReadRetrieveReadApproach
# from approaches.readdecomposeask import ReadDecomposeAsk
# from approaches.chatreadretrieveread import ChatReadRetrieveReadApproach
from azure.storage.blob import BlobServiceClient
from databases import MySQLDatabase, MyLocalSQL
from sqlalchemy import text, create_engine
# from prompts_vivo import prompts_vv
from prompt_main import prompts
#from embs import embeddings

import warnings
warnings.filterwarnings("ignore")

# Replace these with your own values, either in environment variables or directly here
AZURE_STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT") or "mystorageaccount"
AZURE_STORAGE_CONTAINER = os.environ.get("AZURE_STORAGE_CONTAINER") or "content"
AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE") or "cog-gunbku7vcuucu"
AZURE_OPENAI_GPT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_GPT_DEPLOYMENT") or "gpt-35-turbo"
AZURE_OPENAI_CHATGPT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_CHATGPT_DEPLOYMENT") or "chat"
AZURE_OPENAI_CHATGPT_MODEL = os.environ.get("AZURE_OPENAI_CHATGPT_MODEL") or "gpt-35-turbo"
AZURE_OPENAI_EMB_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMB_DEPLOYMENT") or "embedding"


azure_credential = DefaultAzureCredential(exclude_shared_token_cache_credential = True)

# Used by the OpenAI SDK
openai.api_type = "azure"
openai.api_version = "2023-05-15"
openai.api_key = "a9860398e9454aecab048d9e4578e59d"
openai.api_base = "https://cog-gunbku7vcuucu.openai.azure.com/"

connector = MySQLDatabase(
    host="c-rg-cosmosdb-dev.4u3hxce4ykembm.postgres.cosmos.azure.com",
    username="citus",
    password="ntt123_dev",
    database="profuturo",
    port=5432,
    sslmode="require"
)

# connector = MyLocalSQL(db_name='my_local_database.db')

# @timeout(15)  # Set the timeout to 10 seconds
def connecta_sql(query):

    connector.connect()
    result, cols = connector.query(query)
    connector.close()

    return result, cols

def count_tokens(prompt, encoding="cl100k_base"):
    encoding = tiktoken.get_encoding(encoding)
    
    length = len(encoding.encode(prompt))
    # price = (length*0.009713)/1000

    # cost = {
    #     'length': length,
    #     'price (R$)': price
    # }

    return length

def get_embedding(text_to_embed):
	# Embed a line of text
	response = openai.Embedding.create(
    	engine= "text-embedding-ada-002",
    	input=[text_to_embed]
	)
	
	# Extract the AI output embedding as a list of floats
	embedding = response["data"][0]["embedding"]
    
	return embedding

def check_query(question, df_qsts):

    encoded = get_embedding(question)

    embedding_array = np.array(df_qsts['Embeddings'].apply(lambda x: ast.literal_eval(x)).to_list())

    # Compute cosine similarity between 'embedding_new' and all embeddings in 'embeddings_df'
    similarities = cosine_similarity([encoded], embedding_array)

    # Get the index of the most similar sentence
    most_similar_index = similarities.argmax()


    if similarities[0][most_similar_index] >= 0.9:

        # Get the most similar sentence from the DataFrame
        # most_similar_sentence = df.iloc[most_similar_index]["Perguntas"]
        query = df_qsts.iloc[most_similar_index]["Query"]

        return {'result': 1,
        'query':query}

    else:
        return {'result': 0,
        'query':None}


def handle_response_compl(response, quest = True):
    query = response['choices'][0]['text']

    if quest:
        if query.startswith(" "):
            query = "SELECT" + query

    return query

def adapt_query_2(question, query):
    # prompt_adapted = prompts.get('base_prompt').replace('{query}', query).replace('{question}', question).replace('{question}', question)
    prompt_adapted = prompts.get('semi_prompt_1').replace('{query}', query).replace('{question}', question)

    # print(prompt_adapted)

    # try:
    response = openai.Completion.create(
        # engine="chat",
        engine="chat",
        # engine="davinci",
        # engine="chat",
        prompt=prompt_adapted,
        temperature=0.1,
        # temperature=0.1,
        max_tokens=250,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop = ['\n\n', ';', '"']
        # stop=["#", ";", '"', "\\"]
    )
    
    # except Exception as e:
    #     print(f'Problem in checking Question from query: {e}')
    
    # print(response)
    qry = handle_response_compl(response, quest=True)
    response_n = qry.strip()
    response_n = response_n.replace("`", "")

    # Retornar a resposta do modelo
    return response_n

def ids_prompts(question, n_prompt):
    response = ""
    if n_prompt == 1:
        prompt_use = prompts.get("id_prompt_1").replace("{question}", question)
    elif n_prompt == 2:
        prompt_use = prompts.get("id_prompt_2").replace("{question}", question)
    else:
        prompt_use = prompts.get("id_prompt_3").replace("{question}", question)

    try:
        response = openai.Completion.create(
            # engine="chat",
            engine="chat",
            prompt=prompt_use,
            temperature=0.02,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            # best_of=1,
            stop=None
            # stop=["#", ";", '"', "\\"]
        )
    
    except Exception as e:
        print(f'Problem in checking Question in prompt ids_prompts: {e}')
    
    qry = handle_response_compl(response, quest=False)
    response_n = qry.strip()
    response_n = response_n.replace("`", "")

    # Retornar a resposta do modelo
    return response_n

def send_request_openai_query(question, n_queries = 0, former_query = '', query = '', temp = 0.1, att = 1):
    print("estoy en send_request_openai_query")
    response = ""
    print(question)
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     future1 = executor.submit(ids_prompts, question, 1)
    #     future2 = executor.submit(ids_prompts, question, 2)
    #     future3 = executor.submit(ids_prompts, question, 3)

    #     terms_1 = future1.result()
    #     terms_2 = future2.result()
    #     terms_3 = future3.result()
    

    # reasoning = prompts.get('prompt_sql').replace("{reason_1}", terms_1).replace("{reason_2}", terms_2).replace("{reason_3}", terms_3).replace("{quest}", question)
    reasoning = prompts.get('prompt_sql').replace("{question}", question)
    print(reasoning)
    try:
        response = openai.Completion.create(
            # engine="chat",
            engine="chat",
            prompt=reasoning,
            temperature=temp,
            max_tokens=1000,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["#", ";", '"', "\\"]
        )
    except Exception as e:
        print(e)


    query = handle_response_compl(response)
    response_n = query.replace("\n", " ")
    response_n = response_n.replace("`", "")

    # Retornar a resposta do modelo
    return response_n


def send_request_openai_response(result, question, query, att):

    n_tkns = count_tokens(result)
    response_human = ""
    if n_tkns < 700:

        # prompt_r = combine_prompts_2(question, result, query)
        prompt_r = prompts.get("prompt_response_2").replace("{query}", query).replace("{result}", result).replace("{question}", question)

        response_human = openai.Completion.create(
            engine="chat", # chatgpt
            prompt=prompt_r, 
            temperature=0.1,
            max_tokens=1500,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            # stop=[".", "!", "?", "\n", "\n\n"]  
            stop=["#", ";", "\n\n", "\""]
            )
    
        qry = handle_response_compl(response_human, quest=False)
        response_n = qry.strip()
        response_n = response_n.split('\n')[0]
        response_n = response_n.replace("`", "")
    
    else:
        if att == 2:
            response_n = "El alcance de esta pregunta es muy amplio. ¿Podría especificar el alcance de la pregunta?"
        else: 
            response_n = 'none'

    # Retornar a resposta do modelo
    return response_n

def resolving_question_alt(question):

    global final  # Declare secondary_result as global so it can be modified

    #quest = question.upper()
    quest = question
    att = 1
    query = ""
    db_result = ""
    # Filter out rows with None values
    none = 1
    temp = 0.0

    # while att <= 1:
    #     eh_none = False

    #     if att == 1:
    #         temp = 0.0
    #     elif att == 2: 
    #         temp = 0.01
    #     elif att == 3: 
    #         temp = 0.02
    #     elif att == 4: 
    #         temp = 0.07
    #     elif att == 5: 
    #         temp = 0.08
    #     else:
    #         temp = 0.09

    try: 
    # receive question
        print("estoy en resolving_question_alt")
        query = send_request_openai_query(question=quest, temp=temp)
        print(query)
        db_result, _ = connecta_sql(query)
        
        for i in range(len(db_result)):
            if db_result[i][0] == None or db_result[i][0] == 'None,' or db_result[i][0] == 'none' or db_result[i][0] == 'NONE' or db_result[i][0] == '[]' or db_result[i][0] == []:
                none += 1
                # eh_none = True
        
        db_result_final = db_result
        response_from_oai = send_request_openai_response(str(db_result_final), quest, query, att)


        final = {"answer":response_from_oai,
                "sql":query,
                "data":db_result}
        print(final)
        return final
    
    except Exception as e:
        logging.exception('Exception in /question')
        print(f'Tentativa: {att}')
        
        if att == 2:

            final = jsonify({
                    "answer": "Por gentileza, poderia refinar o questionamento feito, ou especificar datas?",
                    "sql": query,
                    "data":db_result
                })
            
            return final
        
        print(att)
        att += 1

        # if isinstance(db_result, list) and len(db_result) == 0:
        #     none += 1
        #     eh_none = True

        # # Access values using their indices
        

        # if none <= 2 and eh_none == False:

        #     if len(db_result) > 3:
        #         db_result_final = db_result[:20] 

        #     else:
        #         db_result_final = db_result 
            
        #     print('Retornou algo.')

        #     response_from_oai = send_request_openai_response(str(db_result_final), quest, query, att)


        #     final = {"answer":response_from_oai,
        #             "sql":query,
        #             "data":db_result}
                
        #     return final
            
        # if none == 2:
        #     print('Retornou None.')
        #     response_from_oai = send_request_openai_response(str(db_result), q, query, att, var)

        #     final = {
        #             "answer": response_from_oai,
        #             "sql": query,
        #             "data":db_result
        #         }
            
        #     return final
        
        # if att == 2:

        #     response_from_oai = send_request_openai_response(str(db_result), q, query, att, var)
        
        #     final = jsonify({
        #             "answer": "Por gentileza, poderia refinar o questionamento feito, ou especificar datas?",
        #             "sql": query,
        #             "data":db_result
        #         }
        #     )

        # return final
    
    

    

def resolving_question(question):

    #df = pd.read_csv('embeddings.csv', encoding='UTF-8')
    # Convert list of dictionaries to DataFrame
    # try:
    #     df = pd.DataFrame(embeddings.get("values"))
    #     df['Embeddings'] = df['Embeddings'].apply(lambda x: ast.literal_eval(x))

    # except Exception as e:
    #     print(e)

    #question = question.upper()

    # query_ok = check_query(question, df)

    print('Se va a resolver.')
    query_ok = resolving_question_alt(question)


    #final_query = adapt_query_2(question.upper(), query_ok['sql'])
    final_query = adapt_query_2(question, query_ok['sql'])
    if 'SELECT' not in final_query:
        final_query = 'SELECT' + final_query

    
    print(final_query)

    db_result, columns = connecta_sql(final_query)

    df = pd.DataFrame(db_result, columns=columns)

    response_from_oai = df.to_html(index=False, classes='table table-striped table-bordered', table_id='my-table', border=1, justify='center', escape=False)

    # Add custom CSS styles for centering rows, setting header color, and making header letters bold
    custom_css = """
        <style>
            table {
                text-align: center;  /* Center align all rows */
            }
            th {
                background-color: blue;  /* Set blue as the header color */
                color: white;  /* Set text color for header */
                font-weight: bold;  /* Make header letters bold */
                text-align: center;
            }
            td {
                vertical-align: middle; /* Center vertically within table cells */
                text-align: center; /* Center horizontally within table cells */
                font-weight: bold;
            }
        </style>
        """

    response_from_oai = response_from_oai + custom_css

    sol1 =  {"answer":response_from_oai,"sql":final_query.replace('\n',''),"data":db_result}
    
    return sol1

question = "¿Cual es el ticket mas reciente que se creo con prioridad 2 - Alta?"
question = "¿Cuantos folios hay de Review en Infraestructura?"
question = "¿Cuantos tickets se generaron del area de Soporte Técnico?"

result = resolving_question(question)
print(result)



# app = Flask(__name__)
# # socketio = SocketIO(app)

# @app.route("/", defaults={"path": "index.html"})
# @app.route("/<path:path>")
# def static_file(path):
#     print(path)
#     return app.send_static_file(path)


# @app.route("/ask", methods=["POST"])
# def ask():
#     #ensure_openai_token()
#     if not request.json:
#         return jsonify({"error": "request must be json"}), 400
#     approach = request.json["approach"]
#     try:
#         impl = ask_approaches.get(approach)
#         if not impl:
#             return jsonify({"error": "unknown approach"}), 400
#         r = impl.run(request.json["question"], request.json.get("overrides") or {})
#         return jsonify(r)
#     except Exception as e:
#         logging.exception("Exception in /ask")
#         return jsonify({"error": str(e)}), 500
    
# @app.route("/talk", methods=["POST"])
# def chat():
#     #ensure_openai_token()
#     if not request.json:
#         return jsonify({"error": "request must be json"}), 400
#     approach = request.json["approach"]
#     try:
#         impl = chat_approaches.get(approach)
#         if not impl:
#             return jsonify({"error": "unknown approach"}), 400
#         r = impl.run(request.json["history"], request.json.get("overrides") or {})
#         return jsonify(r)
#     except Exception as e:
#         logging.exception("Exception in /chat")
#         return jsonify({"error": str(e)}), 500
    
# @app.route("/hello-there", methods=['GET'])
# def howdy():
#     return "General Kenobi..."

# def send_request_openai_test(question):

#     try:
#         response = openai.ChatCompletion.create(
#             engine="chat",
#             # prompt=question,
#             messages=[
#                 {"role": "system", "content": "Hola soy un modelo de AI que responde preguntas de servicenow"},
#                 {"role": "user", "content": question}
#             ],
#             temperature=0,
#             max_tokens=150,
#             frequency_penalty= 0,
#             presence_penalty= 0,
#             request_timeout=25
#             # stop=["#", ";", '"', "\\"]
#         )
#     except Exception as e:
#         print(f'Error sending request to OpenAI: {e}')
    
#     # resp = response['choices'][0]['message']['content']
#     resp = response.choices[0].message.content

#     # Retornar a resposta do modelo
#     return resp

# @app.route("/chat", methods=['POST'])
# def process_question():

#     inicio_req = time.time()
#     if not request.json:
#         return jsonify({"error": "request must be json"}), 400

#     # question = request.json["question"]
#     question = request.json.get('history', '')[-1].get('user', '')
#     print(question)
    
#     result = resolving_question(question)

#     return result

# @app.route("/chat-generate", methods=['POST'])
# def process_question_generating():

#     # inicio_req = time.time()
#     if not request.json:
#         return jsonify({"error": "request must be json"}), 400

#     # question = request.json["question"]
#     question = request.json.get('history', '')[-1].get('user', '')
#     print(question)
    
#     # result = resolving_question(question)
#     result = resolving_question_alt(question)

#     return result


## Ejecucion para pagina web

# if __name__ == "__main__":
#     # app.run()
#     app.run(host="0.0.0.0", port=8888, debug=True)

