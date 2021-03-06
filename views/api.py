import os
from app import app
from config import PLUGINS_REPOSITORY
from flask import (
    json,
    jsonify,
    make_response,
    request,
    send_from_directory
)

# The file that contains json data
PLUGINS_JSON_FILE = os.path.join(PLUGINS_REPOSITORY, "plugins.json")

# The directory which contains plugin files
PLUGINS_DIR = os.path.join(PLUGINS_REPOSITORY, "plugins")

# Load JSON Data
with open(PLUGINS_JSON_FILE) as fp:
    plugins = json.load(fp)['plugins']

dumpCtr = 0


def increase_count(plugin):
    """
    Increments the download count and updates the json file.

    Rather than dumping on every request, the json is dumped
    when the counter reaches a certain value.
    """

    global dumpCtr

    plugin["downloads"] += 1
    dumpCtr += 1
    if dumpCtr >= 50:
        with open(PLUGINS_JSON_FILE, "w") as fp:
            json.dump({'plugins': plugins}, fp)
        dumpCtr = 0


@app.route('/api/v1/', methods=['GET'])
def api_root():
    """
    Shows info about our API
    """
    return make_response(
        jsonify({'message': 'The two endpoints currently available'
                 ' are /api/v1/plugins and /api/v1/download'}), 200)


@app.route('/api/v1/plugins/', methods=['GET'])
def get_plugin():
    """
    Lists data of a plugin
    """

    pid = request.args.get('id', None)
    if pid:
        if pid in plugins:
            plugin = {'plugin': plugins[pid]}
        else:
            return not_found(404)
    else:
        # Show all the plugins if an id is not specified
        plugin = {'plugins': plugins}

    return make_response(jsonify(plugin), 200)


@app.route('/api/v1/download/', methods=['GET'])
def download_plugin():
    """
    Serves files as a download attachment.

    Single files are served as is, multiple ones are zipped.
    """

    pid = request.args.get('id', None)
    if pid:
        if pid in plugins:
            increase_count(plugins[pid])
            return send_from_directory(PLUGINS_DIR, pid + ".zip", as_attachment=True)
        else:
            return not_found(404)
    else:
        return make_response(
            jsonify({'error': 'Plugin id not specified.',
                     'message': 'Correct usage: /api/v1/download?id=<id>'}), 400)


def not_found(error):
    return make_response(jsonify({'error': 'Plugin not found.'}), 404)
