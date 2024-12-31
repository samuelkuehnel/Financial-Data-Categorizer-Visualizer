from flask import Flask, request, render_template, redirect, url_for
import os
from finances import run


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = './'


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file:
            global year
            year = request.form['year']
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                   str(year) + '.csv'))
            global summarized
            sorted_data, summarized = run(year)
            print("Data uploaded")
            return redirect(url_for('display_dataframe'))
    return render_template('index.html')


@app.route('/display-data', methods=['GET'])
def display_dataframe():
    df = summarized
    image_folder = os.path.join('src', 'static', year)
    images = [os.path.join(img)
              for img in os.listdir(image_folder)
              if img.endswith(('jpg', 'jpeg', 'png'))]
    return render_template('displayData.html', tables=[
        df.to_html(border=0, classes='table table-hover', index=False)],
                   titles=df.columns.values,
                   images=enumerate(images), year=year)


app.run(host="0.0.0.0", port=8080)
