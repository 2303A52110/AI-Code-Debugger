from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
load_dotenv()
import requests
from pymongo import MongoClient
import datetime

app = Flask(__name__)

mongo_client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = mongo_client["ai_code_debugger"]
collection = db["history"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        code = request.form['code']
        language = request.form['language']
        level = request.form['level']

        if not code.strip():
            return render_template('index.html', error="Please enter some code.")

        prompt = f"""
You are an expert programming instructor. Explain at a {level} level.
Analyze the following {language} code.

Return your answer in this structured format:
1. Syntax Errors:
2. Logical Errors:
3. Runtime Risks:
4. Corrected Code:
5. Explanation:
6. Optimization Suggestions:
7. Time Complexity:
8. Code Quality Score (out of 10):
9. Learning Tip:

If no syntax errors exist, clearly say: "No syntax errors found."

Code:
{code}
"""

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "nvidia/nemotron-3-super-120b-a12b:free",
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        data = response.json()
        if "choices" not in data:
            raise Exception(str(data))
        result = data["choices"][0]["message"]["content"]

        collection.insert_one({
            "code": code,
            "language": language,
            "result": result,
            "timestamp": datetime.datetime.now()
        })

        return render_template('index.html', result=result)

    except Exception as e:
        return render_template('index.html', error=f"Something went wrong: {str(e)}")

@app.route('/history')
def history():
    records = collection.find().sort("timestamp", -1)
    return render_template('history.html', records=records)

if __name__ == "__main__":
    app.run(debug=False)