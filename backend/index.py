from backend import app

@app.route('/')
def hello():
    return '<html><head></head><body>Backend for <a href="http://publicfields.net">publicfields.net</a>.</body>'
