from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, jsonify
from core.syntax_checker import check_syntax
from core.executor import execute_safe
from core.error_parser import parse_error
from analyzer.rule_engine import analyze_error
from analyzer.concept_mapper import get_concept_explanation
from ai.prompt_builder import build_prompt
from ai.ai_explainer import generate_ai_explanation
from utils.sanitizer import is_safe
from editor.language_config import language_config
from editor.snippets import snippets
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def home():
    return render_template('index.html', config=language_config, snippets=snippets)

@app.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data.get('code', '')
    
    # 1. Sanitize
    safe, msg = is_safe(code)
    if not safe:
        return jsonify({
            "success": False,
            "error": "SecurityViolation",
            "message": msg
        })
    
    # 2. Syntax Check
    syntax_err = check_syntax(code)
    if syntax_err:
        return jsonify({
            "success": False,
            "error": "SyntaxError",
            "details": syntax_err,
            "message": syntax_err['message']
        })

    # 3. Execute
    result = execute_safe(code)
    
    if result['success']:
        return jsonify({
            "success": True,
            "output": result['output']
        })
    else:
        # 4. Error Analysis
        ex_obj = result['exception']
        parsed = parse_error(ex_obj)
        
        # Rule-based
        concept = analyze_error(parsed['type'], parsed['message'])
        basic_expl = get_concept_explanation(concept)
        
        # AI-based
        prompt = build_prompt(code, parsed['details'], concept)
        ai_expl = generate_ai_explanation(prompt)
        
        return jsonify({
            "success": False,
            "error": parsed['type'],
            "message": parsed['message'],
            "traceback": parsed['details'],
            "analysis": {
                "concept": concept,
                "basic_explanation": basic_expl,
                "ai_explanation": ai_expl
            }
        })

if __name__ == '__main__':
    app.run(debug=True)
