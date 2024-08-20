from datetime import datetime
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.now().strftime("%A, %d. %B %Y %I:%M%p"))

if __name__ == '__main__':
    app.run(debug=True)