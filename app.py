import os
from flask import Flask, request, jsonify
from ytmusicapi import YTMusic

app = Flask(__name__)

# Initialize YTMusic for unauthenticated access.
# This instance will be used for both search and general homepage content.
ytmusic = YTMusic()

# You can keep these commented out if you only need unauthenticated features.
# If you ever need personalized content (like "Your Mixes"), you'd uncomment
# and configure the YT_MUSIC_AUTH_JSON environment variable on Render.
# YT_MUSIC_AUTH_JSON = os.environ.get("YT_MUSIC_AUTH_JSON")
# if YT_MUSIC_AUTH_JSON:
#     try:
#         ytmusic_authenticated = YTMusic(json_credentials=YT_MUSIC_AUTH_JSON)
#         print("YTMusicAPI authenticated successfully via JSON string.")
#     except Exception as e:
#         print(f"Error initializing YTMusicAPI with JSON string: {e}")
#         ytmusic_authenticated = None
# else:
#     print("YT_MUSIC_AUTH_JSON not set. Personalized features will not work.")
#     ytmusic_authenticated = None

@app.route('/')
def home():
    """Returns a simple message indicating the API is running."""
    return "YouTube Music API Proxy is running!"

@app.route('/home', methods=['GET'])
def get_ytmusic_home():
    """
    Returns the raw JSON response from ytmusicapi.get_home().
    This is useful for debugging and understanding the full structure
    of the homepage content.
    """
    try:
        # You can adjust the limit based on how much data you want
        homepage_contents = ytmusic.get_home(limit=10) # Increased limit to get more sections
        return jsonify(homepage_contents)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve YouTube Music homepage: {str(e)}"}), 500


@app.route('/featured_playlists', methods=['GET'])
def get_featured_playlists():
    """
    Extracts and returns a filtered list of featured playlists from the
    YouTube Music homepage content.
    """
    try:
        homepage_contents = ytmusic.get_home(limit=10) # Get more sections to find playlists

        extracted_playlists = []
        seen_playlist_ids = set() # To store unique playlist IDs and avoid duplicates

        for section in homepage_contents:
            # Check if the section itself has a resultType of 'playlist' or similar
            if section.get('resultType') == 'playlist' and 'playlistId' in section:
                if section['playlistId'] not in seen_playlist_ids:
                    extracted_playlists.append({
                        "title": section.get('title'),
                        "playlistId": section.get('playlistId'),
                        "thumbnails": section.get('thumbnails'),
                        "author": section.get('author'),
                        "itemCount": section.get('itemCount'),
                        "category": section.get('category'), # Often 'Featured playlists' or similar
                        "source": "section_root" # Indicate where this item was found
                    })
                    seen_playlist_ids.add(section['playlistId'])
            
            # Now iterate through the 'contents' of each section
            if section.get('contents'):
                for item in section['contents']:
                    # Look for items explicitly identified as playlists
                    if item.get('resultType') == 'playlist' and 'playlistId' in item:
                        if item['playlistId'] not in seen_playlist_ids:
                            extracted_playlists.append({
                                "title": item.get('title'),
                                "playlistId": item.get('playlistId'),
                                "thumbnails": item.get('thumbnails'),
                                "author": item.get('author'),
                                "itemCount": item.get('itemCount'),
                                "category": item.get('category'),
                                "source": "section_content" # Indicate where this item was found
                            })
                            seen_playlist_ids.add(item['playlistId'])
                    
                    # Special handling for "Community playlists" or other categories
                    # where the item might be a video but linked to a playlist.
                    # Based on your sample, 'Community playlists' category specifically has
                    # resultType 'playlist' which our first check handles.
                    # The 'Videos' might contain a title like 'Featured playlist by...',
                    # but their resultType is 'video'. We'll stick to actual playlists.

        return jsonify(extracted_playlists)

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve and filter featured playlists: {str(e)}"}), 500

@app.route('/search', methods=['GET'])
def search():
    """
    Performs a YouTube Music search based on the 'query' parameter.
    """
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    try:
        # Search is typically unauthenticated
        results = ytmusic.search(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=os.environ.get('PORT', 5000))
