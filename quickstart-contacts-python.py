# Import your dependencies
from dotenv import load_dotenv
import os
from nylas import Client
from flask import Flask, request, redirect, url_for, session, jsonify
from flask_session.__init__ import Session
from nylas.models.auth import URLForAuthenticationConfig
from nylas.models.auth import CodeExchangeRequest

# Load your env variables
load_dotenv()

# Create the app
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize Nylas client
nylas = Client(
    api_key = os.environ.get("NYLAS_API_KEY"),
    api_uri = os.environ.get("NYLAS_API_URI"),
)

# Call the authorization page
@app.route("/oauth/exchange", methods=["GET"])
def authorized():
    if session.get("grant_id") is None:
        code = request.args.get("code")
        exchangeRequest = CodeExchangeRequest({"redirect_uri": "http://localhost:5000/oauth/exchange",
                                                                                  "code": code,
                                                                                  "client_id": os.environ.get("NYLAS_CLIENT_ID")})
        exchange = nylas.auth.exchange_code_for_token(exchangeRequest)
        session["grant_id"] = exchange.grant_id
        return redirect(url_for("login"))
        
# Main page
@app.route("/nylas/auth", methods=["GET"])
def login():
    if session.get("grant_id") is None:
        config = URLForAuthenticationConfig({"client_id": os.environ.get("NYLAS_CLIENT_ID"), 
                                                                      "redirect_uri" : "http://localhost:5000/oauth/exchange"})
        url = nylas.auth.url_for_oauth2(config)
        return redirect(url)
    else:
        return f'{session["grant_id"]}'

@app.route("/nylas/list-contacts", methods=["GET"])
def list_contacts():
    try:
        query_params = {"limit": 5}
        contacts = nylas.contacts.list(session["grant_id"], query_params=query_params).data
        return jsonify(contacts)
    except Exception as e:
        return f'{e}'

@app.route("/nylas/create-contact", methods=["GET"])
def create_contact():

    request_body = {
        "emails": [{"email": "swag@nylas.com", "type": "work"}],
        "company_name": "Nylas",
        "given_name": "Nylas' Swag",
        "notes": "This is good swag",
        "web_pages": [{"url": "https://www.nylas.com", "type": "work"}]
    }

    try:
        event = nylas.contacts.create(session["grant_id"], 
        request_body = request_body)
        return jsonify(event)
    except Exception as e:
        return f'{e}'

# Run our application
if __name__ == "__main__":
    app.run()
