import os
from dotenv import load_dotenv
from flask import Flask, render_template_string, request, jsonify
from exa_py import Exa

load_dotenv()

app = Flask(__name__)
exa = Exa(api_key=os.getenv("EXA_API_KEY"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Profile Search</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5rem;
        }
        .subtitle {
            color: rgba(255,255,255,0.8);
            text-align: center;
            margin-bottom: 30px;
        }
        .search-box {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        .search-input {
            width: 100%;
            padding: 16px 20px;
            font-size: 18px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            outline: none;
            transition: border-color 0.3s;
        }
        .search-input:focus {
            border-color: #667eea;
        }
        .search-btn {
            width: 100%;
            margin-top: 15px;
            padding: 16px;
            font-size: 18px;
            font-weight: 600;
            color: white;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .search-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        .search-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .examples {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        .examples-title {
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }
        .example-chip {
            display: inline-block;
            padding: 8px 14px;
            margin: 4px;
            background: #f0f0f0;
            border-radius: 20px;
            font-size: 13px;
            color: #555;
            cursor: pointer;
            transition: background 0.2s;
        }
        .example-chip:hover {
            background: #e0e0e0;
        }
        .results {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        }
        .results-header {
            padding: 20px 25px;
            background: #f8f9fa;
            border-bottom: 1px solid #eee;
            font-weight: 600;
            color: #333;
        }
        .profile {
            padding: 20px 25px;
            border-bottom: 1px solid #eee;
            transition: background 0.2s;
        }
        .profile:hover {
            background: #f8f9fa;
        }
        .profile:last-child {
            border-bottom: none;
        }
        .profile-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 6px;
        }
        .profile-title a {
            color: #667eea;
            text-decoration: none;
        }
        .profile-title a:hover {
            text-decoration: underline;
        }
        .profile-url {
            font-size: 13px;
            color: #888;
            word-break: break-all;
        }
        .profile-snippet {
            margin-top: 8px;
            font-size: 14px;
            color: #555;
            line-height: 1.5;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .spinner {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error {
            padding: 20px 25px;
            color: #d32f2f;
            background: #ffebee;
        }
        .no-results {
            padding: 40px 25px;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Profile Search</h1>
        <p class="subtitle">Find people using natural language powered by Exa.ai</p>

        <div class="search-box">
            <form id="searchForm">
                <input type="text" class="search-input" id="query" name="query"
                       placeholder="e.g., VP of Engineering at fintech startups in NYC" required>
                <button type="submit" class="search-btn" id="searchBtn">Search Profiles</button>
            </form>
            <div class="examples">
                <div class="examples-title">Try these examples:</div>
                <span class="example-chip" onclick="setQuery(this)">Machine learning engineers at Google</span>
                <span class="example-chip" onclick="setQuery(this)">Founders of AI startups in San Francisco</span>
                <span class="example-chip" onclick="setQuery(this)">Product managers at Series B companies</span>
                <span class="example-chip" onclick="setQuery(this)">Data scientists with PhD</span>
            </div>
        </div>

        <div id="results"></div>
    </div>

    <script>
        function setQuery(el) {
            document.getElementById('query').value = el.textContent;
        }

        document.getElementById('searchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = document.getElementById('query').value;
            const resultsDiv = document.getElementById('results');
            const btn = document.getElementById('searchBtn');

            btn.disabled = true;
            btn.textContent = 'Searching...';
            resultsDiv.innerHTML = '<div class="results"><div class="loading"><div class="spinner"></div><p style="margin-top:15px">Searching profiles...</p></div></div>';

            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });
                const data = await response.json();

                if (data.error) {
                    resultsDiv.innerHTML = `<div class="results"><div class="error">${data.error}</div></div>`;
                } else if (data.results.length === 0) {
                    resultsDiv.innerHTML = '<div class="results"><div class="no-results">No profiles found. Try a different search.</div></div>';
                } else {
                    let html = `<div class="results"><div class="results-header">Found ${data.results.length} profiles</div>`;
                    data.results.forEach((profile, i) => {
                        html += `
                            <div class="profile">
                                <div class="profile-title">
                                    ${i + 1}. <a href="${profile.url}" target="_blank">${profile.title || 'Untitled Profile'}</a>
                                </div>
                                <div class="profile-url">${profile.url}</div>
                                ${profile.snippet ? `<div class="profile-snippet">${profile.snippet}</div>` : ''}
                            </div>
                        `;
                    });
                    html += '</div>';
                    resultsDiv.innerHTML = html;
                }
            } catch (err) {
                resultsDiv.innerHTML = `<div class="results"><div class="error">Error: ${err.message}</div></div>`;
            }

            btn.disabled = false;
            btn.textContent = 'Search Profiles';
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '')

    if not query:
        return jsonify({'error': 'Please enter a search query'})

    try:
        response = exa.search(
            query=query,
            category="people",
            num_results=10,
            use_autoprompt=True
        )

        results = []
        for result in response.results:
            results.append({
                'title': result.title,
                'url': result.url,
                'snippet': getattr(result, 'snippet', None) or getattr(result, 'text', None)
            })

        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    if not os.getenv("EXA_API_KEY"):
        print("Warning: EXA_API_KEY not set. Create a .env file with your API key.")
    app.run(debug=True, port=5000)
