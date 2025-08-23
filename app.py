from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
	return "<h1>Ubuntus srvr</h1><p>123456</p>"

@app.route("/health")
def health():
	return "OK", 200

#if __name__=="__main__":
#	app.run(host="0.0.0.0", port=5000)
