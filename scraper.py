import praw
import openai
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def get_reddit_data(username):
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    reddit.read_only = True  # read-only access

    user = reddit.redditor(username)
    comments = [c.body for c in user.comments.new(limit=100)]
    posts = [p.title + "\n" + p.selftext for p in user.submissions.new(limit=50)]
    return posts, comments

def generate_persona(posts, comments):
    combined_text = "\n\n".join(posts + comments)
    prompt = f"""
Analyze the following Reddit posts and comments. Generate a detailed user persona.
Include:
- Interests
- Personality traits
- Opinions or beliefs
- Demographics (if guessable)
- Writing style
Cite specific posts/comments used.

Text:
{combined_text[:7000]}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def save_persona(username, persona_text):
    with open(f"persona_{username}.txt", "w", encoding="utf-8") as f:
        f.write(persona_text)

def extract_username(url):
    url = url.strip().rstrip("/")
    return url.split("/")[-1]

def main():
    profile_url = input("Enter Reddit profile URL: ")
    username = extract_username(profile_url)
    print(f"Fetching data for user: {username}...")
    try:
        posts, comments = get_reddit_data(username)
        print("Generating persona using OpenAI...")
        persona = generate_persona(posts, comments)
        print("Saving output to file...")
        save_persona(username, persona)
        print(f"✅ Done! Persona saved to: persona_{username}.txt")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
