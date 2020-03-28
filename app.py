from flask import Flask, render_template, request, send_file
import io, pickle, smtplib, ssl
from azure.storage.blob import BlobServiceClient

connect_str = open('string.txt', 'r').read().rstrip()
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = 'data'
blob_container_client = blob_service_client.get_container_client(container_name)


app = Flask(__name__)

@app.route('/')
def index():
    html = """
    <a href = "/upload_file"> Upload file </a>
    <br/>
    <a href = "/save_text"> Save text </a>
    """
    return html

@app.route('/save_text')
def save_text():
    html = """
    <form action = "/success_text" method = "post">
        <h1> Email </h1>
        <input type = "text" name = "email">
        <h1> Text </h1>
        <input type = "text" name = "text">
        <input type = "submit">
    </form>
    """
    return html    

@app.route('/success_text', methods = ['POST'])
def success_text():
    email = request.form['email']
    text = request.form['text']
    if email == '' or text == '':
        html = """
        Email or text can not be blank.
        <a href = "/save_text"> Try again </a>
        """
        return html
    all_data_for_this_email = update_azure(email, text)
    html = """
    Successfully saved! <br/> <br/>
    Here is all your text so far. We've also sent out an email to you!
 <br/><br/>
    """
    message = """
    Here is a summary of all text you've uploaded so far! """
    
    for d in all_data_for_this_email:
        html = html + d + '<br/>'
        message = message + """ + 
        """ + d + """
        """
   
    #send_email(email, message)
    
    return html



def update_azure(email, data):
    data_dict = pickle.load(io.BytesIO(blob_container_client.get_blob_client('dict.pkl').
               download_blob().readall()))
    blob_container_client.delete_blob('dict.pkl')
    if email not in data_dict:
        data_dict[email] = [data]
    else:
        data_dict[email].append(data)
    blob_container_client.get_blob_client('dict.pkl').upload_blob(
        pickle.dumps(data_dict))
    return data_dict[email]
        


    
if __name__ == '__main__':
    app.run()
