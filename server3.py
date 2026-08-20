from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
	return "Hello, From Server 3!"

app.run(port=5003)