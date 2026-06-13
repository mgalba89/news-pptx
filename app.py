import os
from io import BytesIO

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, send_file, url_for

import ai
import db
import pptx_builder
import scraper

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_db()


@app.route("/")
def index():
    items = db.get_all_items()
    return render_template("index.html", items=items)


@app.route("/add_url", methods=["POST"])
def add_url():
    url = request.form.get("url", "").strip()
    if not url:
        flash("Please enter a URL.", "error")
        return redirect(url_for("index"))
    try:
        text = scraper.fetch_text_from_url(url)
        if not text:
            flash("Could not extract text from the URL.", "error")
            return redirect(url_for("index"))
        summary = ai.summarize_text(text)
        db.add_item("url", url, summary)
        flash("URL added successfully.", "success")
    except Exception as e:
        flash(f"Error processing URL: {e}", "error")
    return redirect(url_for("index"))


@app.route("/add_image", methods=["POST"])
def add_image():
    if "image" not in request.files or request.files["image"].filename == "":
        flash("Please select an image file.", "error")
        return redirect(url_for("index"))
    file = request.files["image"]
    filename = file.filename
    path = os.path.join(UPLOAD_FOLDER, filename)
    try:
        file.save(path)
        summary = ai.summarize_image(path)
        db.add_item("image", filename, summary)
        flash("Image added successfully.", "success")
    except Exception as e:
        flash(f"Error processing image: {e}", "error")
    return redirect(url_for("index"))


@app.route("/generate", methods=["POST"])
def generate():
    date_from = request.form.get("date_from", "").strip()
    date_to = request.form.get("date_to", "").strip()
    if date_from and date_to:
        items = db.get_pending_items_in_range(date_from, date_to)
    else:
        items = db.get_pending_items()
    if not items:
        flash("No pending items found for the selected period.", "error")
        return redirect(url_for("index"))
    try:
        slides_data = ai.generate_presentation_structure(items)
        pptx_bytes = pptx_builder.build_pptx(slides_data)
        db.mark_as_used([item["id"] for item in items])
        return send_file(
            BytesIO(pptx_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            as_attachment=True,
            download_name="news_overview.pptx",
        )
    except Exception as e:
        flash(f"Error generating presentation: {e}", "error")
        return redirect(url_for("index"))


@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    db.delete_item(item_id)
    return ("", 204)


@app.route("/clear", methods=["POST"])
def clear():
    items = db.get_pending_items()
    db.mark_as_used([item["id"] for item in items])
    flash("All pending items marked as used.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
