"""
Mock review data for Find My Gaps analysis.
"""

from typing import List, Dict, Any

# Mock review database
MOCK_REVIEWS = {
    "spotify": [
        {"id": 1, "category": "review", "rating": 2, "text": "Missing lyrics sync feature that Apple Music has. Would pay extra for this.", "source": "app_store", "date": "2025-10-15", "author": "user123"},
        {"id": 2, "category": "review", "rating": 5, "text": "Best music app ever! Love the AI DJ feature.", "source": "app_store", "date": "2025-10-14", "author": "musicfan"},
        {"id": 3, "category": "review", "rating": 3, "text": "Good but needs better podcast discovery. I can't find niche podcasts easily.", "source": "reddit", "date": "2025-10-13", "author": "podcastlover"},
        {"id": 4, "category": "review", "rating": 1, "text": "Terrible shuffle algorithm. Keeps playing same songs. Need better randomization.", "source": "trustpilot", "date": "2025-10-12", "author": "frustrated_user"},
        {"id": 5, "category": "review", "rating": 4, "text": "Great app but missing sleep timer for podcasts. Please add this!", "source": "reddit", "date": "2025-10-11", "author": "sleepy_listener"},
        {"id": 6, "category": "review", "rating": 2, "text": "No way to transfer playlists to other platforms. Lock-in is frustrating.", "source": "app_store", "date": "2025-10-10", "author": "switcher"},
        {"id": 7, "category": "review", "rating": 5, "text": "Discover Weekly is mind-blowing. Always finds music I love.", "source": "app_store", "date": "2025-10-09", "author": "discovery_fan"},
        {"id": 8, "category": "review", "rating": 3, "text": "Needs better audio quality options. Competitors have lossless audio.", "source": "reddit", "date": "2025-10-08", "author": "audiophile"},
        {"id": 9, "category": "review", "rating": 1, "text": "Desktop app is bloated and slow. Takes forever to load.", "source": "trustpilot", "date": "2025-10-07", "author": "desktop_user"},
        {"id": 10, "category": "review", "rating": 4, "text": "Love it but wish there was collaborative queue for parties.", "source": "reddit", "date": "2025-10-06", "author": "party_host"},
        {"id": 11, "category": "review", "rating": 2, "text": "Missing karaoke mode. Would be amazing for social features.", "source": "app_store", "date": "2025-10-05", "author": "karaoke_lover"},
        {"id": 12, "category": "review", "rating": 5, "text": "Interface is clean and intuitive. Easy to use.", "source": "app_store", "date": "2025-10-04", "author": "ux_designer"},
        {"id": 13, "category": "review", "rating": 3, "text": "Need better integration with smart home devices. Alexa support is lacking.", "source": "reddit", "date": "2025-10-03", "author": "smart_home_user"},
        {"id": 14, "category": "review", "rating": 1, "text": "Ads are too frequent on free tier. Unbearable experience.", "source": "trustpilot", "date": "2025-10-02", "author": "free_user"},
        {"id": 15, "category": "review", "rating": 4, "text": "Great but needs concert recommendations based on my music taste.", "source": "reddit", "date": "2025-10-01", "author": "concert_goer"},
        {"id": 31, "category": "review", "rating": 2, "text": "The daily mixes are getting repetitive. Need more variety.", "source": "app_store", "date": "2025-09-30", "author": "mix_user"},
        {"id": 32, "category": "review", "rating": 4, "text": "I love the new UI update, very fresh and modern.", "source": "app_store", "date": "2025-09-29", "author": "designer_fan"},
        {"id": 33, "category": "review", "rating": 3, "text": "Playback issues on Android Auto. Music often cuts out.", "source": "reddit", "date": "2025-09-28", "author": "car_listener"},
        {"id": 45, "category": "review", "rating": 1, "text": "Battery drain is insane, my phone dies in a few hours with Spotify open.", "source": "forum", "date": "2025-09-27", "author": "battery_sufferer"},
        {"id": 46, "category": "review", "rating": 5, "text": "Spotify Connect works flawlessly, great for seamless listening.", "source": "app_store", "date": "2025-09-26", "author": "seamless_listener"},
        {"id": 47, "category": "review", "rating": 3, "text": "Offline downloads are buggy, sometimes my music disappears.", "source": "reddit", "date": "2025-09-25", "author": "offline_user"},
        {"id": 48, "category": "review", "rating": 2, "text": "No option to buy individual songs, only subscribe or listen to ads.", "source": "trustpilot", "date": "2025-09-24", "author": "song_buyer"},
        {"id": 49, "category": "review", "rating": 4, "text": "I really enjoy the curated playlists, always something new to explore.", "source": "app_store", "date": "2025-09-23", "author": "playlist_explorer"},
        {"id": 50, "category": "review", "rating": 1, "text": "The podcast UI is separate and confusing, hard to switch between music and podcasts.", "source": "reddit", "date": "2025-09-22", "author": "podcast_switcher"},
        {"id": 51, "category": "review", "rating": 5, "text": "The sound quality is top-notch, especially with premium.", "source": "app_store", "date": "2025-09-21", "author": "audio_enthusiast"},
        {"id": 52, "category": "review", "rating": 3, "text": "Discovering new artists is difficult without a dedicated 'new releases' section for my tastes.", "source": "forum", "date": "2025-09-20", "author": "new_music_seeker"},
        {"id": 53, "category": "review", "rating": 2, "text": "The social sharing features are very limited, wish I could easily share snippets.", "source": "twitter", "date": "2025-09-19", "author": "social_sharer"},
        {"id": 54, "category": "review", "rating": 4, "text": "Lyrics feature, while not perfect, is a great addition for singing along.", "source": "app_store", "date": "2025-09-18", "author": "karaoke_fan"},
        {"id": 55, "category": "review", "rating": 1, "text": "Too many ads even on paid tier, it's unacceptable.", "source": "trustpilot", "date": "2025-09-17", "author": "premium_ads"},
        {"id": 56, "category": "review", "rating": 5, "text": "Yearly Wrapped is my favorite feature, love seeing my listening habits.", "source": "instagram", "date": "2025-09-16", "author": "wrapped_lover"},
        {"id": 57, "category": "review", "rating": 3, "text": "Needs a better way to filter explicit content for kids' profiles.", "source": "forum", "date": "2025-09-15", "author": "parent_user"},
        {"id": 58, "category": "review", "rating": 2, "text": "The desktop app is constantly crashing, very frustrating.", "source": "reddit", "date": "2025-09-14", "author": "crash_victim"},
        {"id": 59, "category": "review", "rating": 4, "text": "I love the ability to create collaborative playlists with friends.", "source": "app_store", "date": "2025-09-13", "author": "collab_playlist"},
        {"id": 60, "category": "review", "rating": 1, "text": "The volume normalization is off, some songs are way louder than others.", "source": "trustpilot", "date": "2025-09-12", "author": "volume_issues"},
        {"id": 61, "category": "review", "rating": 5, "text": "Student discount is a lifesaver, great value for money.", "source": "app_store", "date": "2025-09-11", "author": "student_saver"},
        {"id": 62, "category": "review", "rating": 3, "text": "The search function is inconsistent, sometimes I get irrelevant results.", "source": "reddit", "date": "2025-09-10", "author": "search_frustration"},
        {"id": 63, "category": "review", "rating": 2, "text": "The autoplay feature after an album ends is annoying, wish I could turn it off permanently.", "source": "forum", "date": "2025-09-09", "author": "autoplay_hater"},
        {"id": 64, "category": "review", "rating": 4, "text": "I appreciate the diverse range of genres and artists available.", "source": "app_store", "date": "2025-09-08", "author": "music_diversity"},
        {"id": 65, "category": "review", "rating": 1, "text": "The customer support is non-existent, took weeks to resolve a billing issue.", "source": "trustpilot", "date": "2025-09-07", "author": "bad_support"},
        {"id": 66, "category": "review", "rating": 5, "text": "Family plan is perfect for sharing music with my whole household.", "source": "app_store", "date": "2025-09-06", "author": "family_user"},
        {"id": 67, "category": "review", "rating": 3, "text": "The queue management is clunky, hard to reorder songs.", "source": "reddit", "date": "2025-09-05", "author": "queue_struggle"},
        {"id": 68, "category": "review", "rating": 2, "text": "Discover Weekly used to be great, now it's just repeating old songs.", "source": "forum", "date": "2025-09-04", "author": "old_discover"},
        {"id": 69, "category": "review", "rating": 4, "text": "I love the new feature that shows upcoming concerts for artists I follow.", "source": "app_store", "date": "2025-09-03", "author": "concert_lover_new"},
        {"id": 70, "category": "review", "rating": 1, "text": "The download limits for offline listening are too restrictive.", "source": "trustpilot", "date": "2025-09-02", "author": "download_limited"},
        {"id": 71, "category": "review", "rating": 5, "text": "The app is incredibly stable, never crashes on my device.", "source": "app_store", "date": "2025-09-01", "author": "stable_app"},
        {"id": 72, "category": "review", "rating": 3, "text": "Podcast recommendations are not tailored to my interests at all.", "source": "reddit", "date": "2025-08-31", "author": "podcast_mismatch"},
        {"id": 73, "category": "review", "rating": 2, "text": "The 'Car Mode' is poorly designed and distracting.", "source": "forum", "date": "2025-08-30", "author": "car_mode_critic"},
        {"id": 74, "category": "review", "rating": 4, "text": "I appreciate the clear labeling of explicit content.", "source": "app_store", "date": "2025-08-29", "author": "explicit_aware"},
        {"id": 75, "category": "review", "rating": 1, "text": "Cannot block annoying artists or songs from my feed.", "source": "trustpilot", "date": "2025-08-28", "author": "block_needed"},
        {"id": 76, "category": "review", "rating": 5, "text": "The crossfade feature works perfectly for smooth transitions.", "source": "app_store", "date": "2025-08-27", "author": "crossfade_fan"},
        {"id": 77, "category": "review", "rating": 3, "text": "The interface is getting cluttered with too many new features.", "source": "reddit", "date": "2025-08-26", "author": "cluttered_ui"},
        {"id": 78, "category": "review", "rating": 2, "text": "My downloaded playlists often fail to load when offline.", "source": "forum", "date": "2025-08-25", "author": "offline_fail"},
        {"id": 79, "category": "review", "rating": 4, "text": "The daily drive playlist is a great mix of news and music.", "source": "app_store", "date": "2025-08-24", "author": "daily_driver"},
        {"id": 80, "category": "review", "rating": 1, "text": "Premium subscription is too expensive for the features offered.", "source": "trustpilot", "date": "2025-08-23", "author": "expensive_premium"},
    ],
    "notion": [
        {"id": 16, "category": "review", "rating": 2, "text": "Mobile app is painfully slow. Takes 5 seconds to open a page.", "source": "app_store", "date": "2025-10-15", "author": "mobile_user"},
        {"id": 17, "category": "review", "rating": 5, "text": "Best note-taking app! So flexible and powerful.", "source": "app_store", "date": "2025-10-14", "author": "power_user"},
        {"id": 18, "category": "review", "rating": 3, "text": "Offline mode is terrible. Can't access anything without internet.", "source": "reddit", "date": "2025-10-13", "author": "traveler"},
        {"id": 19, "category": "review", "rating": 1, "text": "No proper Markdown export. Lock-in is real concern.", "source": "trustpilot", "date": "2025-10-12", "author": "concerned_user"},
        {"id": 20, "category": "review", "rating": 4, "text": "Love it but needs better table functionality. Excel-like features missing.", "source": "reddit", "date": "2025-10-11", "author": "data_person"},
        {"id": 21, "category": "review", "rating": 2, "text": "Collaboration is buggy. Changes don't sync in real-time.", "source": "app_store", "date": "2025-10-10", "author": "team_lead"},
        {"id": 22, "category": "review", "rating": 5, "text": "Templates are amazing. Saved me hours of work.", "source": "app_store", "date": "2025-10-09", "author": "template_fan"},
        {"id": 23, "category": "review", "rating": 3, "text": "Search is terrible. Can't find notes even when I know exact words.", "source": "reddit", "date": "2025-10-08", "author": "searcher"},
        {"id": 24, "category": "review", "rating": 1, "text": "No version history on free plan. Lost important work twice.", "source": "trustpilot", "date": "2025-10-07", "author": "student"},
        {"id": 25, "category": "review", "rating": 4, "text": "Great but needs better calendar integration. Want to see tasks in calendar view.", "source": "reddit", "date": "2025-10-06", "author": "planner"},
        {"id": 34, "category": "review", "rating": 2, "text": "The web clipper is clunky and often misses content.", "source": "chrome_store", "date": "2025-09-27", "author": "clipper_user"},
        {"id": 35, "category": "review", "rating": 5, "text": "Notion has replaced all my other productivity apps.", "source": "twitter", "date": "2025-09-26", "author": "productive_pro"},
        {"id": 36, "category": "review", "rating": 3, "text": "Wish there was a dedicated drawing/sketching tool built-in.", "source": "reddit", "date": "2025-09-25", "author": "artist_user"},
        {"id": 81, "category": "review", "rating": 1, "text": "The desktop app is a memory hog, constantly slowing down my computer.", "source": "forum", "date": "2025-09-24", "author": "memory_hog"},
        {"id": 82, "category": "review", "rating": 5, "text": "I love the database features, so powerful for organizing information.", "source": "app_store", "date": "2025-09-23", "author": "database_lover"},
        {"id": 83, "category": "review", "rating": 3, "text": "Integrating with Google Calendar is a pain, often requires manual syncing.", "source": "reddit", "date": "2025-09-22", "author": "gcal_struggle"},
        {"id": 84, "category": "review", "rating": 2, "text": "Sharing pages with external users is confusing and permissions are tricky.", "source": "trustpilot", "date": "2025-09-21", "author": "sharing_hassle"},
        {"id": 85, "category": "review", "rating": 4, "text": "The dark mode is excellent, easy on the eyes during late-night work.", "source": "app_store", "date": "2025-09-20", "author": "dark_mode_fan"},
        {"id": 86, "category": "review", "rating": 1, "text": "The export options are limited, can't get a clean export to PDF.", "source": "forum", "date": "2025-09-19", "author": "pdf_export_fail"},
        {"id": 87, "category": "review", "rating": 5, "text": "The ability to link pages and create a wiki is a game changer for my team.", "source": "twitter", "date": "2025-09-18", "author": "wiki_builder"},
        {"id": 88, "category": "review", "rating": 3, "text": "The learning curve is steep, took me ages to figure out advanced features.", "source": "reddit", "date": "2025-09-17", "author": "slow_learner"},
        {"id": 89, "category": "review", "rating": 2, "text": "No real-time cursor collaboration, makes pair editing difficult.", "source": "app_store", "date": "2025-09-16", "author": "no_realtime_collab"},
        {"id": 90, "category": "review", "rating": 4, "text": "The inline databases are incredibly versatile and powerful.", "source": "app_store", "date": "2025-09-15", "author": "inline_db_fan"},
        {"id": 91, "category": "review", "rating": 1, "text": "The mobile widget is useless, doesn't show enough information.", "source": "trustpilot", "date": "2025-09-14", "author": "bad_widget"},
        {"id": 92, "category": "review", "rating": 5, "text": "The community templates are a goldmine for new ideas and workflows.", "source": "forum", "date": "2025-09-13", "author": "community_lover"},
        {"id": 93, "category": "review", "rating": 3, "text": "Customizing block colors is limited, wish there were more options.", "source": "reddit", "date": "2025-09-12", "author": "color_critic"},
        {"id": 94, "category": "review", "rating": 2, "text": "The API is hard to use, not well documented for beginners.", "source": "developer_forum", "date": "2025-09-11", "author": "api_struggle"},
        {"id": 95, "category": "review", "rating": 4, "text": "I use Notion for everything, from personal notes to project management.", "source": "app_store", "date": "2025-09-10", "author": "all_in_notion"},
        {"id": 100, "category": "review", "rating": 1, "text": "The free tier is too restrictive, barely usable for anything serious.", "source": "trustpilot", "date": "2025-09-09", "author": "free_tier_complaint"},
        {"id": 101, "category": "review", "rating": 5, "text": "Notion AI is surprisingly good for summarizing and brainstorming.", "source": "twitter", "date": "2025-09-08", "author": "notion_ai_fan"},
        {"id": 102, "category": "review", "rating": 3, "text": "Performance on large pages is terrible, constantly lagging.", "source": "reddit", "date": "2025-09-07", "author": "lag_sufferer"},
        {"id": 103, "category": "review", "rating": 2, "text": "No easy way to duplicate multiple pages at once.", "source": "forum", "date": "2025-09-06", "author": "duplicate_hassle"},
        {"id": 104, "category": "review", "rating": 4, "text": "The command palette is super fast for navigating and actions.", "source": "app_store", "date": "2025-09-05", "author": "command_palette_fan"},
        {"id": 105, "category": "review", "rating": 1, "text": "Customer support is slow and unhelpful, took weeks to get a response.", "source": "trustpilot", "date": "2025-09-04", "author": "bad_support_notion"},
        {"id": 106, "category": "review", "rating": 5, "text": "I love the flexibility of creating my own systems and workflows.", "source": "app_store", "date": "2025-09-03", "author": "workflow_creator"},
        {"id": 107, "category": "review", "rating": 3, "text": "The mobile app often crashes when trying to open complex pages.", "source": "reddit", "date": "2025-09-02", "author": "mobile_crash"},
        {"id": 108, "category": "review", "rating": 2, "text": "No option for handwritten notes or sketching.", "source": "forum", "date": "2025-09-01", "author": "no_handwriting"},
        {"id": 109, "category": "review", "rating": 4, "text": "The embedding feature for various apps is fantastic.", "source": "app_store", "date": "2025-08-31", "author": "embed_fan"},
        {"id": 110, "category": "review", "rating": 1, "text": "The notification system is broken, I miss critical updates.", "source": "trustpilot", "date": "2025-08-30", "author": "broken_notifications"},
        {"id": 111, "category": "review", "rating": 5, "text": "Notion is the ultimate tool for personal knowledge management.", "source": "twitter", "date": "2025-08-29", "author": "pkm_expert"},
        {"id": 112, "category": "review", "rating": 3, "text": "The web app consumes too much RAM, my browser struggles.", "source": "reddit", "date": "2025-08-28", "author": "ram_hog"},
        {"id": 113, "category": "review", "rating": 2, "text": "Calendar view needs more features, like recurring tasks.", "source": "forum", "date": "2025-08-27", "author": "calendar_limitations"},
        {"id": 114, "category": "review", "rating": 4, "text": "The search filter options are powerful once you understand them.", "source": "app_store", "date": "2025-08-26", "author": "search_master"},
        {"id": 115, "category": "review", "rating": 1, "text": "The pricing tiers are confusing and expensive for small teams.", "source": "trustpilot", "date": "2025-08-25", "author": "pricing_confusion"},
        {"id": 116, "category": "review", "rating": 5, "text": "Notion is constantly improving and adding valuable features.", "source": "app_store", "date": "2025-08-24", "author": "innovative_app"},
        {"id": 117, "category": "review", "rating": 3, "text": "The comment system is basic, needs more rich text formatting.", "source": "reddit", "date": "2025-08-23", "author": "comment_needs_rich_text"},
        {"id": 118, "category": "review", "rating": 2, "text": "No integration with popular email clients for task creation.", "source": "forum", "date": "2025-08-22", "author": "email_integration_missing"},
        {"id": 119, "category": "review", "rating": 4, "text": "The ability to customize icons and covers makes pages feel personal.", "source": "app_store", "date": "2025-08-21", "author": "customization_lover"},
        {"id": 120, "category": "review", "rating": 1, "text": "Offline access is still a major pain point, frequently fails to load content.", "source": "trustpilot", "date": "2025-08-20", "author": "offline_again"},
    ],
    "slack": [
        {"id": 26, "category": "review", "rating": 2, "text": "Missing AI summarization of long threads. Would save so much time.", "source": "trustpilot", "date": "2025-10-15", "author": "busy_manager"},
        {"id": 27, "category": "review", "rating": 5, "text": "Best team communication tool. Can't imagine work without it.", "source": "app_store", "date": "2025-10-14", "author": "remote_worker"},
        {"id": 28, "category": "review", "rating": 3, "text": "Needs better video call quality. Zoom is much better.", "source": "reddit", "date": "2025-10-13", "author": "video_caller"},
        {"id": 29, "category": "review", "rating": 1, "text": "Search is useless after 90 days on free plan. Ridiculous limitation.", "source": "trustpilot", "date": "2025-10-12", "author": "free_tier_user"},
        {"id": 30, "category": "review", "rating": 4, "text": "Love it but need better thread organization. Hard to follow conversations.", "source": "reddit", "date": "2025-10-11", "author": "thread_follower"},
        {"id": 37, "category": "review", "rating": 2, "text": "Notifications are inconsistent, sometimes I miss important messages.", "source": "app_store", "date": "2025-09-24", "author": "missed_message_user"},
        {"id": 38, "category": "review", "rating": 5, "text": "Integrations with other tools are seamless and powerful.", "source": "g2_crowd", "date": "2025-09-23", "author": "integration_fan"},
        {"id": 39, "category": "review", "rating": 1, "text": "Too many channels, it's hard to keep track of everything.", "source": "reddit", "date": "2025-09-22", "author": "overwhelmed_user"},
        {"id": 121, "category": "review", "rating": 3, "text": "The desktop app is a resource hog, constantly draining my laptop battery.", "source": "forum", "date": "2025-09-21", "author": "battery_drain_slack"},
        {"id": 122, "category": "review", "rating": 5, "text": "Emoji reactions are a simple but effective way to acknowledge messages.", "source": "app_store", "date": "2025-09-20", "author": "emoji_lover"},
        {"id": 123, "category": "review", "rating": 2, "text": "The file sharing limit is too low on the free plan, always running out of space.", "source": "trustpilot", "date": "2025-09-19", "author": "file_limit_user"},
        {"id": 124, "category": "review", "rating": 4, "text": "Slack Huddles are a great quick way to connect with teammates.", "source": "app_store", "date": "2025-09-18", "author": "huddle_fan"},
        {"id": 125, "category": "review", "rating": 1, "text": "The mobile app is buggy, messages often fail to send or load.", "source": "reddit", "date": "2025-09-17", "author": "mobile_bug_slack"},
        {"id": 126, "category": "review", "rating": 5, "text": "I love the ability to customize notifications per channel.", "source": "app_store", "date": "2025-09-16", "author": "custom_notify"},
        {"id": 127, "category": "review", "rating": 3, "text": "The search functionality is not as robust as I'd like, hard to find old conversations.", "source": "forum", "date": "2025-09-15", "author": "search_struggle_slack"},
        {"id": 128, "category": "review", "rating": 2, "text": "Too many distracting notifications, wish there was a 'focus mode'.", "source": "twitter", "date": "2025-09-14", "author": "distracted_user"},
        {"id": 129, "category": "review", "rating": 4, "text": "Slack Connect has made external collaboration so much easier.", "source": "app_store", "date": "2025-09-13", "author": "slack_connect_fan"},
        {"id": 130, "category": "review", "rating": 1, "text": "The new UI changes are confusing and less intuitive.", "source": "reddit", "date": "2025-09-12", "author": "ui_critic_slack"},
        {"id": 131, "category": "review", "rating": 5, "text": "The ability to schedule messages is a lifesaver for different time zones.", "source": "app_store", "date": "2025-09-11", "author": "scheduler_fan"},
        {"id": 132, "category": "review", "rating": 3, "text": "Voice messages are not easily searchable or transcribable.", "source": "forum", "date": "2025-09-10", "author": "voice_message_issue"},
        {"id": 133, "category": "review", "rating": 2, "text": "The automatic channel suggestions are often irrelevant.", "source": "trustpilot", "date": "2025-09-09", "author": "bad_suggestions"},
        {"id": 134, "category": "review", "rating": 4, "text": "I appreciate the wide range of app integrations available.", "source": "app_store", "date": "2025-09-08", "author": "integration_lover_slack"},
        {"id": 135, "category": "review", "rating": 1, "text": "The pricing structure for larger teams is too expensive.", "source": "trustpilot", "date": "2025-09-07", "author": "expensive_slack"},
        {"id": 136, "category": "review", "rating": 5, "text": "The shared channels feature is great for working with external partners.", "source": "app_store", "date": "2025-09-06", "author": "shared_channels_fan"},
        {"id": 137, "category": "review", "rating": 3, "text": "The thread view can be overwhelming with very active channels.", "source": "reddit", "date": "2025-09-05", "author": "thread_overload"},
        {"id": 138, "category": "review", "rating": 2, "text": "Video call quality is consistently poor, often drops out.", "source": "forum", "date": "2025-09-04", "author": "poor_video_slack"},
        {"id": 139, "category": "review", "rating": 4, "text": "The ability to set reminders is very useful for keeping track of tasks.", "source": "app_store", "date": "2025-09-03", "author": "reminder_fan"},
        {"id": 140, "category": "review", "rating": 1, "text": "The mobile app constantly logs me out, very inconvenient.", "source": "trustpilot", "date": "2025-09-02", "author": "mobile_logout_issue"},
        {"id": 141, "category": "review", "rating": 5, "text": "Slack's custom emojis are a great way to add personality to conversations.", "source": "app_store", "date": "2025-09-01", "author": "custom_emoji_lover"},
        {"id": 142, "category": "review", "rating": 3, "text": "The search results are not always chronological, making it hard to find recent info.", "source": "reddit", "date": "2025-08-31", "author": "search_order_issue"},
        {"id": 143, "category": "review", "rating": 2, "text": "The desktop app startup time is very slow, especially after an update.", "source": "forum", "date": "2025-08-30", "author": "slow_startup_slack"},
        {"id": 144, "category": "review", "rating": 4, "text": "I like the simple and clean interface of Slack.", "source": "app_store", "date": "2025-08-29", "author": "clean_ui_slack"},
        {"id": 145, "category": "review", "rating": 1, "text": "The file preview feature is often broken or takes too long to load.", "source": "trustpilot", "date": "2025-08-28", "author": "broken_preview"},
        {"id": 146, "category": "review", "rating": 5, "text": "The ability to quickly share code snippets with proper formatting is amazing.", "source": "app_store", "date": "2025-08-27", "author": "code_sharer"},
        {"id": 147, "category": "review", "rating": 3, "text": "The DMs often get lost in the sea of channels, need better visibility.", "source": "reddit", "date": "2025-08-26", "author": "dm_visibility"},
        {"id": 148, "category": "review", "rating": 2, "text": "The 'away' status isn't always accurate, sometimes I appear online when I'm not.", "source": "forum", "date": "2025-08-25", "author": "inaccurate_status"},
        {"id": 149, "category": "review", "rating": 4, "text": "I appreciate the security features and admin controls.", "source": "app_store", "date": "2025-08-24", "author": "security_fan_slack"},
        {"id": 150, "category": "review", "rating": 1, "text": "The constant updates are disruptive and often introduce new bugs.", "source": "trustpilot", "date": "2025-08-23", "author": "update_hater_slack"},
    ],
    "netflix": [
        {"id": 40, "category": "review", "rating": 3, "text": "Too many reboots and not enough original new content.", "source": "twitter", "date": "2025-10-15", "author": "old_school_viewer"},
        {"id": 41, "category": "review", "rating": 5, "text": "Love the variety of international shows and movies!", "source": "app_store", "date": "2025-10-14", "author": "world_cinema_fan"},
        {"id": 42, "category": "review", "rating": 2, "text": "The recommendation engine is terrible, always suggests things I don't like.", "source": "reddit", "date": "2025-10-13", "author": "picky_viewer"},
        {"id": 43, "category": "review", "rating": 4, "text": "Great for binge-watching, but wish there was a 'skip intro' for every show.", "source": "trustpilot", "date": "2025-10-12", "author": "binge_watcher"},
        {"id": 44, "category": "review", "rating": 1, "text": "Price keeps going up, but content quality is declining. Not worth it anymore.", "source": "app_store", "date": "2025-10-11", "author": "budget_user"},
        {"id": 151, "category": "review", "rating": 5, "text": "The user interface is intuitive and easy to navigate.", "source": "app_store", "date": "2025-10-10", "author": "ui_lover_netflix"},
        {"id": 152, "category": "review", "rating": 2, "text": "The subtitles are often out of sync, making it hard to follow.", "source": "reddit", "date": "2025-10-09", "author": "subtitle_struggle"},
        {"id": 153, "category": "review", "rating": 4, "text": "Offline downloads work perfectly for travel.", "source": "app_store", "date": "2025-10-08", "author": "traveler_netflix"},
        {"id": 154, "category": "review", "rating": 1, "text": "Too many ads now, even for premium subscribers.", "source": "trustpilot", "date": "2025-10-07", "author": "premium_ads_netflix"},
        {"id": 155, "category": "review", "rating": 3, "text": "Wish there was a better way to filter content by language.", "source": "forum", "date": "2025-10-06", "author": "language_filter_needed"},
        {"id": 156, "category": "review", "rating": 5, "text": "The 4K streaming quality is incredible on my big screen TV.", "source": "app_store", "date": "2025-10-05", "author": "4k_viewer"},
        {"id": 157, "category": "review", "rating": 2, "text": "The continue watching section is buggy, often shows completed shows.", "source": "reddit", "date": "2025-10-04", "author": "buggy_continue"},
        {"id": 158, "category": "review", "rating": 4, "text": "Love the profiles feature for personalized recommendations.", "source": "app_store", "date": "2025-10-03", "author": "profile_fan"},
        {"id": 159, "category": "review", "rating": 1, "text": "Customer service is unresponsive, terrible experience.", "source": "trustpilot", "date": "2025-10-02", "author": "bad_support_netflix"},
        {"id": 160, "category": "review", "rating": 3, "text": "The mobile app constantly buffers, even on fast internet.", "source": "reddit", "date": "2025-10-01", "author": "buffering_user"},
        {"id": 161, "category": "review", "rating": 5, "text": "Netflix documentaries are always high quality and informative.", "source": "app_store", "date": "2025-09-30", "author": "docu_fan"},
        {"id": 162, "category": "review", "rating": 2, "text": "The search function is limited, hard to find obscure titles.", "source": "forum", "date": "2025-09-29", "author": "limited_search_netflix"},
        {"id": 163, "category": "review", "rating": 4, "text": "I enjoy the interactive stories and games.", "source": "app_store", "date": "2025-09-28", "author": "interactive_fan"},
        {"id": 164, "category": "review", "rating": 1, "text": "The kids' profiles don't always filter out inappropriate content effectively.", "source": "trustpilot", "date": "2025-09-27", "author": "kids_filter_fail"},
        {"id": 165, "category": "review", "rating": 3, "text": "Wish there was an option to sort by release date for new content.", "source": "reddit", "date": "2025-09-26", "author": "sort_by_date_needed"},
        {"id": 166, "category": "review", "rating": 5, "text": "The ability to adjust playback speed is a fantastic feature.", "source": "app_store", "date": "2025-09-25", "author": "speed_control_fan"},
        {"id": 167, "category": "review", "rating": 2, "text": "The download size for movies is too large, quickly fills up my device.", "source": "forum", "date": "2025-09-24", "author": "large_downloads"},
        {"id": 168, "category": "review", "rating": 4, "text": "Love the option to set a PIN for profiles.", "source": "app_store", "date": "2025-09-23", "author": "pin_protection"},
        {"id": 169, "category": "review", "rating": 1, "text": "The auto-play of trailers on the home screen is annoying.", "source": "trustpilot", "date": "2025-09-22", "author": "trailer_hater"},
        {"id": 170, "category": "review", "rating": 3, "text": "Needs better integration with smart TV remote controls.", "source": "reddit", "date": "2025-09-21", "author": "smart_tv_integration"},
        {"id": 171, "category": "review", "rating": 5, "text": "The variety of regional content is excellent.", "source": "app_store", "date": "2025-09-20", "author": "regional_content_fan"},
        {"id": 172, "category": "review", "rating": 2, "text": "The app crashes frequently on my smart TV.", "source": "forum", "date": "2025-09-19", "author": "smart_tv_crash"},
        {"id": 173, "category": "review", "rating": 4, "text": "I appreciate the consistent release of new original series.", "source": "app_store", "date": "2025-09-18", "author": "original_series_fan"},
        {"id": 174, "category": "review", "rating": 1, "text": "The pricing tiers are complex and confusing.", "source": "trustpilot", "date": "2025-09-17", "author": "confusing_pricing_netflix"},
        {"id": 175, "category": "review", "rating": 3, "text": "Wish there was a watchlist sharing feature.", "source": "reddit", "date": "2025-09-16", "author": "watchlist_sharing"},
        {"id": 176, "category": "review", "rating": 5, "text": "The 'remind me' feature for upcoming shows is very helpful.", "source": "app_store", "date": "2025-09-15", "author": "remind_me_fan"},
        {"id": 177, "category": "review", "rating": 2, "text": "The audio description feature is not available for many titles.", "source": "forum", "date": "2025-09-14", "author": "audio_description_missing"},
        {"id": 178, "category": "review", "rating": 4, "text": "Love the ability to skip credits automatically.", "source": "app_store", "date": "2025-09-13", "author": "skip_credits_fan"},
        {"id": 179, "category": "review", "rating": 1, "text": "The buffering issues make it unwatchable sometimes.", "source": "trustpilot", "date": "2025-09-12", "author": "unwatchable_buffering"},
        {"id": 180, "category": "review", "rating": 3, "text": "Needs more options for parental controls, beyond just profiles.", "source": "reddit", "date": "2025-09-11", "author": "advanced_parental_controls"},
        {"id": 181, "category": "review", "rating": 5, "text": "The interactive content keeps me engaged.", "source": "app_store", "date": "2025-09-10", "author": "engaged_viewer"},
        {"id": 182, "category": "review", "rating": 2, "text": "The search results are not always relevant to my query.", "source": "forum", "date": "2025-09-09", "author": "irrelevant_search_results"},
        {"id": 183, "category": "review", "rating": 4, "text": "I like the 'Top 10 in your country' feature for discovering popular shows.", "source": "app_store", "date": "2025-09-08", "author": "top10_fan"},
        {"id": 184, "category": "review", "rating": 1, "text": "The limited number of simultaneous streams is frustrating for families.", "source": "trustpilot", "date": "2025-09-07", "author": "limited_streams"},
        {"id": 185, "category": "review", "rating": 3, "text": "Wish there was an option to permanently hide content I've already watched.", "source": "reddit", "date": "2025-09-06", "author": "hide_watched_content"},
        {"id": 186, "category": "review", "rating": 5, "text": "The picture-in-picture mode on mobile is very convenient.", "source": "app_store", "date": "2025-09-05", "author": "pip_fan"},
        {"id": 187, "category": "review", "rating": 2, "text": "The app sometimes freezes when I try to cast to my TV.", "source": "forum", "date": "2025-09-04", "author": "casting_freeze"},
        {"id": 188, "category": "review", "rating": 4, "text": "The quality of original movies has improved significantly.", "source": "app_store", "date": "2025-09-03", "author": "improved_movies"},
        {"id": 189, "category": "review", "rating": 1, "text": "The lack of new popular movies is disappointing.", "source": "trustpilot", "date": "2025-09-02", "author": "no_new_movies"},
        {"id": 190, "category": "review", "rating": 3, "text": "The UI sometimes feels clunky and slow to respond.", "source": "reddit", "date": "2025-09-01", "author": "clunky_ui_netflix"},
    ]
}


def get_reviews(company: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get mock reviews for a company.
    
    Args:
        company: Company name (lowercase)
        limit: Maximum number of reviews
    
    Returns:
        List of review dictionaries
    """
    company = company.lower()
    if company not in MOCK_REVIEWS:
        return []
    
    return MOCK_REVIEWS[company][:limit]


def get_all_companies() -> List[str]:
    """Get list of companies with mock reviews."""
    return list(MOCK_REVIEWS.keys())


def get_reviews_by_rating(company: str, min_rating: int = 1, max_rating: int = 5) -> List[Dict[str, Any]]:
    """
    Get reviews filtered by rating range.
    
    Args:
        company: Company name
        min_rating: Minimum rating (1-5)
        max_rating: Maximum rating (1-5)
    
    Returns:
        Filtered reviews
    """
    reviews = get_reviews(company)
    return [r for r in reviews if min_rating <= r["category": "review", "rating"] <= max_rating]


def get_reviews_by_source(company: str, source: str) -> List[Dict[str, Any]]:
    """
    Get reviews from specific source.
    
    Args:
        company: Company name
        source: Source name (app_store, reddit, trustpilot)
    
    Returns:
        Filtered reviews
    """
    reviews = get_reviews(company)
    return [r for r in reviews if r["source"] == source]


def search_reviews(company: str, keyword: str) -> List[Dict[str, Any]]:
    """
    Search reviews by keyword.
    
    Args:
        company: Company name
        keyword: Search keyword
    
    Returns:
        Matching reviews
    """
    reviews = get_reviews(company)
    keyword_lower = keyword.lower()
    return [r for r in reviews if keyword_lower in r["text"].lower()]

