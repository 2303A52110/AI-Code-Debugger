from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import requests
import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Optional MongoDB (safe)
collection = None
try:
    
    mongo_uri = os.getenv("MONGO_URI")
    
except:
    collection = None


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

        # Better error handling
        if response.status_code != 200:
            return render_template('index.html', error=f"API Error: {response.text}")

        data = response.json()

        if "choices" not in data:
            return render_template('index.html', error="Invalid API response")

        result = data["choices"][0]["message"]["content"]

        # Save history if MongoDB exists
        

        return render_template('index.html', result=result)

    except Exception as e:
        return render_template('index.html', error=f"Error: {str(e)}")


@app.route('/history')
def history():
    return render_template('history.html', records=[])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)