from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# === 🔐 AUTH SERVICE ===
@app.route("/auth/login", methods=["POST"])
def proxy_login():
    return proxy("http://authservice:5000/login")

@app.route("/auth/register", methods=["POST"])
def proxy_register():
    return proxy("http://authservice:5000/register")

@app.route("/auth/profile", methods=["GET"])
def proxy_profile():
    return proxy("http://authservice:5000/profile", method="GET")

@app.route("/auth/settings", methods=["POST"])
def proxy_settings():
    return proxy("http://authservice:5000/settings")


# === 🧾 INVOICE SERVICE ===
@app.route("/invoice/upload", methods=["POST"])
def proxy_upload_invoice():
    return proxy("http://invoiceservice:5001/upload")

@app.route("/invoice/check_filename", methods=["POST"])
def proxy_check_filename():
    return proxy("http://invoiceservice:5001/check_filename")

@app.route("/invoice/view", methods=["GET"])
def proxy_invoice_view():
    return proxy("http://invoiceservice:5001/view", method="GET")

@app.route("/invoice/view_data_by_date", methods=["GET"])
def proxy_view_by_date():
    return proxy("http://invoiceservice:5001/view_data_by_date", method="GET")

@app.route("/invoice/view_invoices_by_month", methods=["GET"])
def proxy_by_month():
    return proxy("http://invoiceservice:5001/view_invoices_by_month", method="GET")


# === 🔄 SPLIT SERVICE ===
@app.route("/split/add_user", methods=["POST"])
def proxy_add_split_user():
    return proxy("http://splitservice:5002/add_split_user")

@app.route("/split/my_users", methods=["GET"])
def proxy_my_split_users():
    return proxy("http://splitservice:5002/my_split_users", method="GET")

@app.route("/split/invoice", methods=["POST"])
def proxy_split_invoice():
    return proxy("http://splitservice:5002/split_invoice")

@app.route("/split/invoice/<bill_id>", methods=["GET"])
def proxy_get_split_details(bill_id):
    return proxy(f"http://splitservice:5002/split_invoice/{bill_id}", method="GET")

@app.route("/split/api/split_users", methods=["GET"])
def proxy_api_split_users():
    return proxy("http://splitservice:5002/api/split_users", method="GET")

@app.route("/split/api/split_items/<bill_id>", methods=["GET"])
def proxy_api_split_items(bill_id):
    return proxy(f"http://splitservice:5002/api/split_items/{bill_id}", method="GET")


# === 💸 SETTLEMENT SERVICE ===
@app.route("/settlement/settle", methods=["POST"])
def proxy_settle():
    return proxy("http://settlementservice:5003/settle")

@app.route("/settlement/summary", methods=["GET"])
def proxy_summary():
    return proxy("http://settlementservice:5003/summary", method="GET")

@app.route("/settlement/log", methods=["GET"])
def proxy_log():
    return proxy("http://settlementservice:5003/settlement_log", method="GET")

@app.route("/settlement/debts", methods=["GET"])
def proxy_debts():
    return proxy("http://settlementservice:5003/debts", method="GET")

@app.route("/settlement/api/debts/<bill_id>", methods=["GET"])
def proxy_debt_by_bill(bill_id):
    return proxy(f"http://settlementservice:5003/api/debts/{bill_id}", method="GET")


# === 📊 BALANCE SERVICE ===
@app.route("/balance/my", methods=["GET"])
def proxy_my_balance():
    return proxy("http://balanceservice:5004/my_balances", method="GET")

@app.route("/balance/summary", methods=["GET"])
def proxy_balance_summary():
    return proxy("http://balanceservice:5004/balance_summary", method="GET")

@app.route("/balance/owed_by", methods=["GET"])
def proxy_owed_by():
    return proxy("http://balanceservice:5004/owed_by", method="GET")

@app.route("/balance/owe_to", methods=["GET"])
def proxy_owe_to():
    return proxy("http://balanceservice:5004/owe_to", method="GET")


# === 🔁 Proxy Handler ===
def proxy(url, method="POST"):
    try:
        if method == "GET":
            resp = requests.get(url, headers=request.headers, params=request.args)
        else:
            resp = requests.post(url, headers=request.headers, json=request.get_json())
        return (resp.content, resp.status_code, resp.headers.items())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return jsonify({"message": "API Gateway is live."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
