"""Paint app with a JSON API.

Endpoints:
  GET  /                 -> the paint UI (HTML)
  GET  /api/state       -> {"version": N, "strokes": [...], "image": "dataurl"|null}
  POST /api/stroke      -> {"points": [[x,y],...], "color": "#rrggbb", "size": 5}
  POST /api/clear       -> clears all strokes
  POST /api/save       -> {"path": "..."}  render strokes to a PNG
  POST /api/load       -> {"path": "..."}  load a PNG as the background image
  GET  /api/health     -> {"ok": true}
"""
import io
import threading
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image, ImageDraw

app = Flask(__name__)

CANVAS_W, CANVAS_H = 900, 600

_lock = threading.Lock()
_state = {"version": 0, "strokes": [], "image": None}  # image = data URL or None


def _render_png(strokes, image_dataurl=None):
    """Render strokes (and optional background image) to a PNG bytes object."""
    if image_dataurl:
        # data:image/png;base64,xxxx
        b64 = image_dataurl.split(",", 1)[1]
        import base64
        img = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA")
        img = img.resize((CANVAS_W, CANVAS_H))
    else:
        img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)
    for s in strokes:
        color = s.get("color", "#000000")
        size = max(1, int(s.get("size", 5)))
        pts = s.get("points", [])
        if len(pts) >= 2:
            draw.line([(p[0], p[1]) for p in pts], fill=color, width=size)
        elif len(pts) == 1:
            x, y = pts[0]
            draw.ellipse([x - size/2, y - size/2, x + size/2, y + size/2], fill=color)

    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


@app.get("/api/health")
def health():
    return jsonify(ok=True)


@app.get("/api/state")
def state():
    with _lock:
        return jsonify(dict(_state))


@app.post("/api/stroke")
def add_stroke():
    data = request.get_json(force=True, silent=True) or {}
    points = data.get("points")
    color = data.get("color", "#000000")
    size = data.get("size", 5)
    if not points:
        return jsonify(error="points required"), 400
    with _lock:
        _state["strokes"].append({"points": points, "color": color, "size": size})
        _state["version"] += 1
        version = _state["version"]
    return jsonify(ok=True, version=version)


@app.post("/api/clear")
def clear():
    with _lock:
        _state["strokes"] = []
        _state["image"] = None
        _state["version"] += 1
        version = _state["version"]
    return jsonify(ok=True, version=version)


@app.post("/api/save")
def save():
    path = (request.get_json(force=True, silent=True) or {}).get("path", "paint.png")
    with _lock:
        png = _render_png(_state["strokes"], _state["image"])
    with open(path, "wb") as f:
        f.write(png)
    return jsonify(ok=True, path=path)


@app.post("/api/load")
def load():
    path = (request.get_json(force=True, silent=True) or {}).get("path")
    if not path:
        return jsonify(error="path required"), 400
    try:
        img = Image.open(path).convert("RGBA")
    except Exception as e:
        return jsonify(error=f"cannot open {path}: {e}"), 400
    img = img.resize((CANVAS_W, CANVAS_H))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    import base64
    dataurl = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    with _lock:
        _state["image"] = dataurl
        _state["strokes"] = []
        _state["version"] += 1
        version = _state["version"]
    return jsonify(ok=True, version=version)


@app.get("/")
def index():
    return send_from_directory("templates", "index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5177, debug=False)
