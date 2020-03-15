from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify
import json
import os.path, dropbox

app = Flask(__name__)
app.secret_key = 'h432hi5ohi3h5i5hi3o2hi'
API_KEY = 'BT1HAVEIyxAAAAAAAAAA5oAv6eADnABFoSz9-5Ma1bjaaSCZ9L_9_CNkwbHMLznC'
dbx_client = dropbox.Dropbox(API_KEY)
@app.route('/')
def home():
    return render_template('home.html', codes=session.keys())


class TransferData:
    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, f, file_to):
        """upload a file to Dropbox using API v2
        """
        dbx = dropbox.Dropbox(self.access_token)

        dbx.files_upload(f.read(), file_to)
transferData = TransferData(API_KEY)

@app.route('/your-url', methods=['GET','POST'])
def your_url():
    if request.method == 'POST':
        urls = {}

        if os.path.exists('urls.json'):
            with open('urls.json') as urls_file:
                urls = json.load(urls_file)

        if request.form['code'] in urls.keys():
            flash('That short name has already been taken. Please select another name.')
            return redirect(url_for('home'))

        if 'url' in request.form.keys():
            urls[request.form['code']] = {'url':request.form['url']}
        else:
            f = request.files['file']
            full_name = request.form['code'] + f.filename
#            f.save(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + full_name)
#            file_from = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + full_name
            file_to = '/' + full_name
            transferData.upload_file(f, file_to)
            urls[request.form['code']] = {'file':full_name}


        with open('urls.json','w') as url_file:
            json.dump(urls, url_file)
            session[request.form['code']] = True
        return render_template('your_url.html', code=request.form['code'])
    else:
        return redirect(url_for('home'))

@app.route('/<string:code>')
def redirect_to_url(code):
    if os.path.exists('urls.json'):
        with open('urls.json') as urls_file:
            urls = json.load(urls_file)
            if code in urls.keys():
                if 'url' in urls[code].keys():
                    return redirect(urls[code]['url'])
                else:
                    return redirect(url_for('static', filename='user_files/' + urls[code]['file']))
    return abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.route('/api')
def session_api():
    return jsonify(list(session.keys()))
