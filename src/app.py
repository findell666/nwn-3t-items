from flask import Flask, render_template, request, redirect, send_file
import os
import time
import baseLib
import csvExport
import string, random
import pathlib

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = "./tmp"


def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def format_server_time():
    server_time = time.localtime()
    return time.strftime("%I:%M:%S %p", server_time)

@app.route('/')
def index():
    pa1 = pathlib.Path(__file__).parent.absolute
    pa2 = os.getcwd()  

    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))    

    context = { 'server_time' : format_server_time(), 'pa1': str(pa1), 'pa2': str(pa2)}
    return render_template('index.html', context=context)

@app.route('/test', methods=['POST'])    
def test():    
    if request.method == 'POST':
        if 'pcfile' not in request.files:
            return redirect('/')
        file = request.files['pcfile']
        if file:                    
            filename = randomString(12)+".bic"        
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            theList = baseLib.rawGetItems(filename)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            context = { 'list_items' : theList}
            return render_template('items.html', context=context)
            
@app.route('/exportToCSV', methods=['POST'])    
def exportToCSV():    
    if request.method == 'POST':
        if 'pcfile' not in request.files:
            return redirect('/')
        files = request.files.getlist('pcfile')
        files = list(files)
        if files:

            params = {}
            #expands
            params["expand_skills"] = True if None != request.form.get("expand_skills") else False
            params["expand_uses"] = True if None != request.form.get("expand_uses") else False
            params["expand_abilities"] = True if None != request.form.get("expand_abilities") else False
            params["expand_dr"] = True if None != request.form.get("expand_dr") else False
            params["expand_saves"] = True if None != request.form.get("expand_saves") else False
            #filters
            params["filter_scrolls"] = True if None != request.form.get("filter_scrolls") else False
            params["filter_potions"] = True if None != request.form.get("filter_potions") else False
            params["filter_keys"] = True if None != request.form.get("filter_keys") else False
            params["filter_trinkets"] = True if None != request.form.get("filter_trinkets") else False
            params["filter_blank_scroll"] = True if None != request.form.get("filter_blank_scroll") else False
            params["filter_gems"] = True if None != request.form.get("filter_gems") else False
            params["filter_bag"] = True if None != request.form.get("filter_bag") else False
            params["filter_owner"] = True if None != request.form.get("filter_owner") else False
            #excludes
            params["exclude_equips"] = True if None != request.form.get("exclude_equips") else False

            params["group_duplicates"] = True if None != request.form.get("group_duplicates") else False

            originalFileNames = []
            filesToProcess = []
            #save the files in tmp
            for i in range(len(files)):
                file = files[i]
                originalFileName = file.filename
                originalFileNames.append(originalFileName)                
                filename = randomString(12)+".bic"        
                filesToProcess.append(filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


            csvFileName = csvExport.runExportAsCSV(filesToProcess, app.config['UPLOAD_FOLDER'], originalFileNames, params)

            for i in range(len(filesToProcess)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filesToProcess[i]))

            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], csvFileName), as_attachment=True)

        return redirect('/')            
    return redirect('/')        

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


