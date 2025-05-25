from flask import Flask, request, jsonify, send_from_directory, render_template
import os
from dfa_generate import regex_to_dfa, simulate_dfa_path, draw_dfa, create_gif_from_frames

app = Flask(__name__)
FRAMES_DIR = "dfa_frames"
os.makedirs(FRAMES_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/draw_dfa", methods=["POST"])
def api_draw_dfa():
    data = request.json
    regex = data.get("regex")
    if not regex:
        return jsonify({"error": "Missing regex"}), 400
    dfa = regex_to_dfa(regex)
    image_filename = "dfa_diagram"
    image_path = os.path.join(FRAMES_DIR, image_filename)
    draw_dfa(dfa, image_path)
    print(regex)
    return jsonify({"image_url": f"/dfa_frames/{image_filename}"})

@app.route("/dfa_frames/<filename>")
def serve_frame(filename):
    return send_from_directory(FRAMES_DIR, filename)

@app.route('/hello')
def hello():
    return 'Hello, World!'

@app.route("/api/validate_dfa", methods=["POST"])
def api_validate_dfa():
    data = request.json
    regex = data.get("regex")
    input_str = data.get("input_string")
    if not regex or not input_str:
        return jsonify({"error": "Missing regex or input string"}), 400

    dfa = regex_to_dfa(regex)
    try:
        path, accepted = simulate_dfa_path(dfa, input_str)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Generate frames for animation
    frames_dir = FRAMES_DIR
    for i in range(len(path)):
        current_edge = [path[i]]
        # Highlight the destination state of the current edge
        highlight_states = [str(path[i][2])]
        draw_dfa(
            dfa,
            os.path.join(frames_dir, f'frame_{i}'),
            path=current_edge,
            input_str=input_str,
            current_index=i,
            highlight_states=highlight_states
        )
    gif_filename = "dfa_animation.gif"
    create_gif_from_frames(frames_dir, output_file=os.path.join(frames_dir, gif_filename), duration=1000)
    # Clean up frames
    for file in os.listdir(frames_dir):
        if file.startswith("frame_") and file.endswith(".png"):
            os.remove(os.path.join(frames_dir, file))
    # Generate the full path image
    full_path_filename = "dfa_diagram_path.png"
    draw_dfa(
        dfa,
        os.path.join(frames_dir, "dfa_diagram_path"),
        path=path,
        input_str=input_str,
        current_index=None,
        highlight_states=[str(state[2]) for state in path]  # Highlight all states in the path
    )
    return jsonify({
        "result": "Valid" if accepted else "Invalid",
        "gif_url": f"/dfa_frames/{gif_filename}",
        "full_path_url": f"/dfa_frames/{full_path_filename}"
    })

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500