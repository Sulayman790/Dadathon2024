from flask import Flask, request, jsonify, render_template_string
import boto3
import json

app = Flask(__name__)

def generate_overview_prompt(company_name):
    prompt = {
        "role": "system",
        "content": "You are a financial advisor for a financial analyst. Answer in English.",
        "instructions": {
            "company_name": company_name,
            "overview": {
                "introduction": "Briefly introduce the company.",
                "board_of_directors": "List the members of the Board of Directors, starting with the Chairman.",
                "board_committees": "Detail the various committees of the Board (e.g., audit, nomination, governance, etc.).",
                "executive_team": "Present the executive team members with their roles and responsibilities."
            }
        }
    }
    return json.dumps(prompt, indent=4, ensure_ascii=False)

def generate_strategy_prompt(company_name):
    prompt = {
        "role": "system",
        "content": "You are a financial advisor for a financial analyst. Answer in English.",
        "instructions": {
            "company_name": company_name,
            "strategy_and_risk": {
                "annual_report": "Analyze the company's strategy and key business risks based on the annual report.",
                "financial_metrics": [
                    "Net margin (%)",
                    "ROE (Return on Equity)",
                    "Immediate liquidity ratio",
                    "Interest coverage ratio",
                    "Debt/EBITDA ratio",
                    "EPS growth rate",
                    "PER (Price-to-Earnings Ratio)",
                    "EV/EBITDA",
                    "Free Cash Flow Yield",
                    "Dividend Yield (%)",
                    "Global ESG Score",
                    "Market share comparison",
                    "Market share changes",
                    "Strategic investments and new products",
                    "Crisis resilience"
                ]
            }
        }
    }
    return json.dumps(prompt, indent=4, ensure_ascii=False)

def invoke_bedrock_agent(prompt_json):
    try:
        client = boto3.client(
            service_name='bedrock-agent-runtime',
            region_name='us-west-2',
            aws_access_key_id="AKIAR2QID37NBSCXNSWA",
            aws_secret_access_key="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"
        )
        
        agent_id = 'LZ3IIASMX8'
        agent_alias_id = '6LPDL4ANZH'
        session_id = "46c53a4c-da98-48c6-ac6c-925948d8fc45"
        
        messages_payload = {
            "messages": [
                {"role": "user", "content": f"Here is the JSON prompt for the company: {prompt_json}"}
            ],
            "max_tokens": 2000
        }

        payload = json.dumps(messages_payload)

        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=payload,
        )
        completion = ""
        for event in response.get("completion"):
            completion += event["chunk"]["bytes"].decode("utf-8")
        print(completion)

        if completion:
            return completion
        else:
            return "No response generated."
    except Exception as e:
        print(f"Error invoking Bedrock agent: {e}")
        return {"error": str(e)}

# HTML intégré pour l'interface utilisateur
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial AI Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #ffffff;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .search-container {
            width: 100%;
            max-width: 800px;
            padding: 20px;
            background: #1e1e1e;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
            border-radius: 8px;
            text-align: center;
            margin-top: 50px;
        }
        .search-bar {
            width: calc(100% - 100px);
            padding: 10px;
            font-size: 16px;
            border: 1px solid #333;
            border-radius: 4px;
            background-color: #333;
            color: #fff;
        }
        .query-type {
            margin-top: 10px;
            margin-bottom: 10px;
            font-size: 16px;
            padding: 5px;
            border-radius: 4px;
        }
        .search-button {
            padding: 10px 15px;
            font-size: 16px;
            cursor: pointer;
            border: none;
            color: #fff;
            background-color: #FF9800;
            border-radius: 4px;
            margin-left: 10px;
        }
        .results {
            margin-top: 20px;
            text-align: left;
            background-color: #2e2e2e;
            padding: 15px;
            border-radius: 8px;
            max-height: 300px;
            overflow-y: auto;
            overflow-wrap: break-word;
            width: calc(100% - 40px);
            white-space: pre-wrap;
            font-family: monospace;
            color: #ffffff;
            word-break: break-word;
        }
    </style>
</head>
<body>
    <img src="/static/images/logo_finance.png" alt="logo_finance" class="logo" width="150">
    <div class="search-container">
        <h2>Financial AI Assistant</h2>
        <select id="queryType" class="query-type">
            <option value="overview">Overview</option>
            <option value="strategy">Strategy & Risks</option>
        </select>
        <input type="text" id="searchInput" class="search-bar" placeholder="Enter the company name...">
        <button onclick="searchQuery()" class="search-button">Search</button>
        <div id="results" class="results"></div>
    </div>

    <script>
        async function searchQuery() {
            const query = document.getElementById("searchInput").value;
            const queryType = document.getElementById("queryType").value;
            
            const response = await fetch(`/search`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ query, queryType })
            });
            const data = await response.json();
            document.getElementById("results").innerHTML = `<pre>${data.result}</pre>`;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_code)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    company_name = data.get("query", "")
    query_type = data.get("queryType", "overview")

    if company_name:
        if query_type == "overview":
            prompt_json = generate_overview_prompt(company_name)
        elif query_type == "strategy":
            prompt_json = generate_strategy_prompt(company_name)
        
        result = invoke_bedrock_agent(prompt_json)
        return jsonify({"result": result})
    else:
        return jsonify({"result": "No company name provided"}), 400

if __name__ == '__main__':
    app.run(debug=True)