from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>SecureAuth MFA Demo</h1>
    <p>Multi-Factor Authentication Demo Application</p>
    <p>Application is running successfully.</p>
    """


if __name__ == "__main__":
    app.run(debug=True)