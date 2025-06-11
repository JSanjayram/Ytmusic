import os
from flask import Flask, request, jsonify
from ytmusicapi import YTMusic

app = Flask(__name__)

# Initialize YTMusic for unauthenticated access.
# This will allow you to get general featured playlists.
# For personalized featured playlists (like "Your mix 1", "Discover Mix"),
# you would need authentication.
ytmusic = YTMusic()

# If you wanted personalized featured playlists, you'd enable this:
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
    return "YouTube Music API Proxy is running!"

@app.route('/featured_playlists', methods=['GET'])
def get_featured_playlists():
    try:
        # Get the home page content
        # The 'limit' parameter controls how many "shelves" or sections to retrieve.
        # Each shelf can contain different types of content (playlists, albums, artists, etc.)
        homepage_contents = ytmusic.get_home(limit=5) # Get 5 sections from the homepage

        featured_playlists = []
        for section in homepage_contents:
            if section.get('contents'):
                for item in section['contents']:
                    # Check if the item is a playlist and extract its details
                    if item.get('resultType') == 'playlist' or 'playlistId' in item:
                        # You might want to filter further, e.g., by title keywords
                        # if 'featured' is in item.get('title', '').lower():
                        featured_playlists.append({
                            "title": item.get('title'),
                            "playlistId": item.get('playlistId'),
                            "thumbnails": item.get('thumbnails'),
                            "author": item.get('author'),
                            "itemType": item.get('resultType')
                        })
                    elif item.get('title') and "playlist" in item.get('title', '').lower() and 'contents' in item:
                        # Sometimes a section itself can be a playlist-like container
                        # with a list of songs/videos, but not explicitly a 'playlist' resultType.
                        # You'd need to inspect the structure returned by get_home carefully.
                        pass


        # You might have duplicates if a playlist appears in multiple sections.
        # To get unique playlists, you can use a set of playlistIds:
        unique_playlists = {}
        for pl in featured_playlists:
            if pl.get('playlistId'):
                unique_playlists[pl['playlistId']] = pl
        
        return jsonify(list(unique_playlists.values()))

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve featured playlists: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=os.environ.get('PORT', 5000))
