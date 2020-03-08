import bottle

from bottle import run, get, template, request, route, post, static_file, error


def check_login(username, password):
    if username is 'M' and password is 'A':
        return True

# Route or Get links the ('/hello/') to the hello function
# i.e it links an URL to a callback function
@get('/hello')
def hello():
    return 'Hello World'

# You can bind more than one route to a single callback
# a wildcard is a -name enclosed in a bracket- i.e <name>
# wildcard can be used as variable
@route('/')
@get('/hello/<name>')
def greet(name='Stranger'):
    return template('Hello {{name}}, how are you?', name=name)

# HTTP Request
# used either as method= or stand alone
# @post @put @delete @patch

# Displays a HTML form
@get('/login') # or @route('/login')
def login():
    return '''
        <form action="/login" method="post">
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            <input value="Login" type="submit" />
        </form>
    '''
# This is invoked on the previous callback
@post('/login') # or @route('/login', method='POST')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    print(username)
    print(password)
    if check_login(username, password) is True:
        print(True)
        return "<p>Your login information was correct.</p>"
    else:
        return "<p>Login failed.</p>"

# Static files such as images or CSS files are not served automatically.
# You have to add a route and a callback to control which files get served and where to find them.
# the <filename:path> filter is used for files in the sub-directory because <filename> does not match a path with a /.
@route('/static/<filename:path>')
def server_static(filename):
    return static_file(filename, root='/path/to/your/static/files')

# 404
@error(404)
def error():
    return "<p> Nothing to see here <p>"

# The run() is always the last line and starts a built-in development server.
#
run(host='localhost', port=8080, debug=True)