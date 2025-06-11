import os
from flask import Flask, request, jsonify
from ytmusicapi import YTMusic #, OAuthCredentials # Only import if using OAuth

app = Flask(__name__)

# --- YTMusicAPI Authentication Setup ---
# It's best practice to pass credentials as environment variables
# You can store the content of your browser.json as a single environment variable
# If using oauth, store client_id, client_secret, etc. separately.

YT_MUSIC_AUTH_JSON = os.environ.get("YT_MUSIC_AUTH_JSON")

if YT_MUSIC_AUTH_JSON:
    # ytmusicapi can take the content of the JSON directly as a string
    # or you can write it to a temporary file in /tmp
    # For simplicity, let's assume it can take the string directly or we convert it.
    # Note: The 'browser.json' structure is what ytmusicapi expects.
    # We'll provide it as a string for Render.
    try:
        # If ytmusicapi can take the raw JSON string directly:
        ytmusic_authenticated = YTMusic(json_credentials=YT_MUSIC_AUTH_JSON)
        print("YTMusicAPI authenticated successfully via JSON string.")
    except Exception as e:
        print(f"Error initializing YTMusicAPI with JSON string: {e}")
        ytmusic_authenticated = None # Fallback or handle error
else:
    print("YT_MUSIC_AUTH_JSON environment variable not set. Authenticated functions will fail.")
    ytmusic_authenticated = None

ytmusic_unauthenticated = YTMusic() # For unauthenticated calls

# --- API Endpoints ---

@app.route('/')
def home():
    return "YouTube Music API Proxy is running!"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    try:
        results = ytmusic_unauthenticated.search(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    if not ytmusic_authenticated:
        return jsonify({"error": "Authentication not set up for playlist creation"}), 401

    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')

    if not title:
        return jsonify({"error": "Title is required"}), 400

    try:
        playlist_id = ytmusic_authenticated.create_playlist(title, description)
        return jsonify({"message": "Playlist created", "playlist_id": playlist_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # For local development
    app.run(debug=True, port=os.environ.get('PORT', 5000))
