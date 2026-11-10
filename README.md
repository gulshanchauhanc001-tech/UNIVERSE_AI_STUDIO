# UNIVERSE AI STUDIO

A dark, creator-focused AI filmmaking workspace built with Streamlit and Supabase.

## Current features

- Email OTP and Google OAuth sign-in through Supabase Auth.
- Project-scoped AI memory for scenes, characters, locations and dialogue.
- Film Studio prompt workspace with independent Auto / Manual / Custom controls for:
  - Duration
  - Quality
  - Aspect ratio
  - Visual style
  - Camera
  - Voice and emotion
  - Music and sound
  - Subtitles
- Template Library with reusable YouTube-friendly creative formats (Shorts hooks, anime, horror, storytime, mini vlogs, explainers, comedy, gaming, product showcases and more).
- Create, save, reuse and delete personal templates.
- Private project Asset Library backed by Supabase Storage.
- Storyboard and JSON project export.

## Important capability note

This repository currently prepares prompts and production plans. It does **not** include a connected video-generation, image-to-video, voice-synthesis, lip-sync or final MP4-rendering provider. Those features require separate provider accounts, API credentials and integration work. The interface must not imply that a video has rendered when it has only prepared a prompt.

## Run locally

1. Install Python 3.11 or newer.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create `.streamlit/secrets.toml` (never commit this file):

   ```toml
   [supabase]
   url = "https://YOUR_PROJECT.supabase.co"
   anon_key = "YOUR_SUPABASE_ANON_KEY"
   redirect_url = "http://localhost:8501"
   ```

4. Configure the Supabase database and private Storage bucket using `supabase_setup.sql`.
5. Start the app:

   ```bash
   streamlit run app.py
   ```

## Deploy on Streamlit Community Cloud

- Repository: `gulshanchauhanc001-tech/UNIVERSE_AI_STUDIO`
- Branch: `main`
- Main file: `app.py`
- Python: 3.11 or newer
- Add the same `[supabase]` values in the app's Streamlit Secrets settings.
- Set the Supabase Auth redirect URL to the deployed Streamlit app URL and add that URL to Supabase Auth's allowed redirect URLs.

A push to the connected GitHub repository normally triggers an app update. Dependency changes trigger a full environment reinstall. See the [Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) and [secrets guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

## Required Supabase tables

The app expects:
- `ai_memory`: `user_id`, `project_name`, `memory_type`, `title`, `content`, `created_at`.
- `studio_assets`: `user_id`, `project_name`, `bucket_id`, `file_path`, `file_name`, `file_type`, `mime_type`, `size_bytes`, `created_at`.
- A private Storage bucket named `studio-assets`.

The SQL setup file creates these objects and enables per-user row/storage policies. Review it against any existing production schema before applying it to a database with existing data.

## Security

- Never put Supabase keys, OAuth client secrets, provider API keys or `secrets.toml` in Git.
- Use the Supabase anon/public key only in the client app with correctly configured Row Level Security. Never use a service-role key in this app.
- Configure Google OAuth credentials and callback URLs in Supabase Auth separately.
