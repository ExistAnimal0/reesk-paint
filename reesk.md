# Reesk Paint

A minimal paint app with a JSON API. Draw in the browser, or drive it programmatically.

## Run

```
cd c:\projects\paint_app
python app.py
```

UI: http://127.0.0.1:5177/
API: http://127.0.0.1:5177/api/*

## API

| Method | Path          | Body                              | Returns                          |
|--------|---------------|-----------------------------------|----------------------------------|
| GET    | /api/health   | —                                 | `{"ok": true}`                   |
| GET    | /api/state    | —                                 | `{"version", "strokes", "image"}`|
| POST   | /api/stroke   | `{"points", "color", "size"}`     | `{"ok", "version"}`              |
| POST   | /api/clear    | `{}`                              | `{"ok", "version"}`              |
| POST   | /api/save     | `{"path"}`                        | `{"ok", "path"}`                 |
| POST   | /api/load     | `{"path"}`                        | `{"ok", "version"}`              |

### Stroke

```json
{
  "points": [[x, y], [x, y], ...],
  "color":  "#rrggbb",
  "size":   5
}
```

- `points` — array of `[x, y]` canvas coordinates (0–900, 0–600).
- `color` — hex color string.
- `size` — stroke width in pixels (1–60).

### Save / Load

- **Save** renders all strokes (plus any loaded background) to a PNG at `path`.
- **Load** sets a PNG file as the background image and clears existing strokes.

## Canvas

900 × 600 px. White background by default.

## Files

```
paint_app/
  app.py              Flask server + API
  templates/
    index.html        Paint UI (canvas + toolbar)
  out.png             last saved render
```
