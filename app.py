"""Simple API service that needs rate limiting added.

This is a basic HTTP API for a URL shortener service.
Currently has NO rate limiting - that's what we're adding!
"""

from flask import Flask, request, jsonify, redirect
import hashlib
import time
from typing import Dict, Optional

app = Flask(__name__)

# In-memory storage for URL mappings
url_store: Dict[str, str] = {}
url_stats: Dict[str, int] = {}


def shorten_url(long_url: str) -> str:
    """Generate a short hash for a URL."""
    hash_object = hashlib.md5(long_url.encode())
    return hash_object.hexdigest()[:8]


@app.route("/shorten", methods=["POST"])
def create_short_url():
    """Create a shortened URL.

    TODO: Add rate limiting here - 10 requests per minute per user.
    """
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in request"}), 400

    long_url = data["url"]
    user_id = data.get("user_id", "anonymous")

    # TODO: Check rate limit here
    # if not rate_limiter.allow_request(user_id):
    #     return jsonify({"error": "Rate limit exceeded"}), 429

    short_code = shorten_url(long_url)
    url_store[short_code] = long_url
    url_stats[short_code] = 0

    return jsonify({
        "short_url": f"http://short.url/{short_code}",
        "long_url": long_url
    })


@app.route("/<short_code>", methods=["GET"])
def redirect_to_url(short_code: str):
    """Redirect to the original URL.

    TODO: Add rate limiting here - 100 requests per minute per user.
    """
    user_id = request.args.get("user_id", "anonymous")

    # TODO: Check rate limit here
    # if not rate_limiter.allow_request(user_id):
    #     return jsonify({"error": "Rate limit exceeded"}), 429

    if short_code not in url_store:
        return jsonify({"error": "URL not found"}), 404

    url_stats[short_code] += 1
    return redirect(url_store[short_code])


@app.route("/stats/<short_code>", methods=["GET"])
def get_stats(short_code: str):
    """Get statistics for a shortened URL."""
    if short_code not in url_store:
        return jsonify({"error": "URL not found"}), 404

    return jsonify({
        "short_code": short_code,
        "long_url": url_store[short_code],
        "clicks": url_stats[short_code]
    })


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "urls_stored": len(url_store)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
