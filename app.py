from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, jsonify
from core.syntax_checker import check_syntax
from core.executor import execute_safe
from core.error_parser import parse_error_from_stderr
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


def _json_error(status=500, error="", message="", line=None, **kwargs):
    """Always return a JSON response for errors. Never HTML."""
    payload = {
        "success": False,
        "status": "runtime_error" if status >= 500 else "compile_error",
        "output": "",
        "error": error or message,
        "message": message or error,
        "line": line,
        **kwargs,
    }
    return jsonify(payload), status


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
def json_error_handler(e):
    """Ensure Flask never returns HTML error pages."""
    code = getattr(e, "code", 500)
    msg = getattr(e, "description", str(e)) if hasattr(e, "description") else str(e)
    return _json_error(status=code, error=type(e).__name__, message=msg, line=None)


@app.errorhandler(Exception)
def catch_all_error(e):
    """Catch any unhandled exception and return JSON."""
    return _json_error(
        status=500,
        error=type(e).__name__,
        message=str(e),
        line=None,
    )


@app.route('/')
def home():
    return render_template('index.html', config=language_config, snippets=snippets)


@app.route('/run', methods=['POST'])
def run_code():
    try:
        data = request.get_json(silent=True) or {}
        code = data.get('code', '')
    except Exception as e:
        return _json_error(status=400, error="BadRequest", message=str(e), line=None)

    # 1. Sanitize
    safe, msg = is_safe(code)
    if not safe:
        return jsonify({
            "success": False,
            "status": "compile_error",
            "output": "",
            "error": "SecurityViolation",
            "message": msg,
            "line": None,
        })

    # 2. Syntax Check
    syntax_err = check_syntax(code)
    if syntax_err:
        return jsonify({
            "success": False,
            "status": "compile_error",
            "output": "",
            "error": "SyntaxError",
            "message": syntax_err.get("message", "Syntax error"),
            "line": syntax_err.get("line"),
        })

    # 3. Execute (subprocess)
    result = execute_safe(code)

    if result['success']:
        return jsonify({
            "success": True,
            "status": "success",
            "output": result.get('output', ''),
            "error": None,
            "line": None,
        })

    # 4. Runtime error or timeout – parse stderr
    stderr = result.get('stderr', '')
    parsed = parse_error_from_stderr(stderr) if stderr else None

    if parsed:
        concept = analyze_error(parsed['type'], parsed['message'])
        basic_expl = get_concept_explanation(concept)
        prompt = build_prompt(code, parsed['details'], concept)
        ai_expl = generate_ai_explanation(prompt)
    else:
        concept = "UNKNOWN_ERROR"
        basic_expl = ""
        ai_expl = stderr or "An error occurred."
        parsed = {
            "type": result.get("error_type", "RuntimeError"),
            "message": result.get("error_message", stderr),
            "details": stderr,
            "line": result.get("line"),
        }

    return jsonify({
        "success": False,
        "status": "runtime_error",
        "output": result.get('output', ''),
        "error": parsed['type'],
        "message": parsed['message'],
        "line": parsed.get('line'),
        "traceback": parsed.get('details'),
        "analysis": {
            "concept": concept,
            "basic_explanation": basic_expl,
            "ai_explanation": ai_expl,
        },
    })


if __name__ == '__main__':
    app.run(debug=True)
