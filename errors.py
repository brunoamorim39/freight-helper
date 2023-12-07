from flask import jsonify, render_template

from __init__ import app, dynamodb

@app.errorhandler(404)
def _404(error):
    '''
    404 Error handler
    '''
    print(error)
    return render_template('errors/404.html'), 404

@app.errorhandler(413)
def _413(error):
    '''
    413 Error handler
    '''
    print(error)
    return 'File is too large', 413