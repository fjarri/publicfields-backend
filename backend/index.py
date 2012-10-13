from backend import app

@app.route('/')
def hello():
    return '<html><head></head><body>Backend for <a href="publicfields.net">publicfields.net</a>.</body>'
