from flask import Flask, jsonify, render_template, send_from_directory
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/folders')
def list_folders():
    base_path = './outputs'
    folders = [f for f in os.listdir(
        base_path) if os.path.isdir(os.path.join(base_path, f))]
    return jsonify(folders)


@app.route('/outputs/<path:filename>')
def serve_file(filename):
    return send_from_directory('outputs', filename)


if __name__ == '__main__':
    app.run(debug=True)
