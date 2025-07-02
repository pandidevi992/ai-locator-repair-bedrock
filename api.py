from flask import Flask, jsonify
from tests.test_sample import run_test_case

app = Flask(__name__)

@app.route("/run-test", methods=["POST"])
def trigger_test():
    try:
        run_test_case()
        return jsonify({"status": "success", "message": "Test case executed."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
