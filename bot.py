import telebot
import requests

TELEGRAM_BOT_TOKEN = '8813599857:AAHAjxTWRKTu1C0uXAgTn-WGE-FDwvPqRcA'
CHANNEL_ID = '@Mazketli'
TMDB_API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwMWZiMzM1OWEyZDQyZDVkZjlkMGZhODM1MjBmMmY0MiIsIm5iZiI6MTc4MjA2NzM2NC4xMjksInN1YiI6IjZhMzgzMGE0MDVlMGUzNzk4ZmU0NzFjNCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.xfni5xNoZpEptcLzVmRCRF_26lqZ7bq_sPXWC4Ivicc'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def get_movie_details(movie_name):
    search_url = f"https://api.themoviedb.org/3/search/movie?query={movie_name}&language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_KEY}"
    }
    try:
        response = requests.get(search_url, headers=headers).json()
        if not response.get('results'):
            return None
        movie_data = response['results'][0]
        movie_id = movie_data['id']
        
        details_url_en = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
        movie_details_en = requests.get(details_url_en, headers=headers).json()
        
        details_url_ar = f"https://api.themoviedb.org/3/movie/{movie_id}?language=ar"
        movie_details_ar = requests.get(details_url_ar, headers=headers).json()
        
        title_en = movie_details_en.get('original_title', movie_name)
        release_date = movie_details_en.get('release_date', '')
        year = release_date.split('-')[0] if release_date else 'N/A'
        rating = round(movie_details_en.get('vote_average', 0), 1)
        
        overview = movie_details_ar.get('overview', '')
        if not overview or overview == "":
            overview = movie_details_en.get('overview', 'لا توجد قصة متوفرة حالياً.')
            
        poster_path = movie_details_en.get('poster_path', '')
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
        
        genres = [g['name'] for g in movie_details_en.get('genres', [])]
        genres_str = " | ".join(genres) if genres else "N/A"
        
        return {
            'title_en': title_en,
            'year': year,
            'rating': rating,
            'genres': genres_str,
            'overview': overview,
            'poster': poster_url
        }
    except Exception:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a movie name in English.")

@bot.message_handler(func=lambda message: True)
def handle_movie_request(message):
    movie_name = message.text
    bot.reply_to(message, f"🔍 Searching for: {movie_name}...")
    movie = get_movie_details(movie_name)
    if not movie:
        bot.reply_to(message, "❌ Movie not found.")
        return
        
    caption = (
        f"🎬 **{movie['title_en']}**\n"
        f"___\n"
        f"📊 التقييم: {movie['rating']} / 10\n"
        f"📅 سنة الإنتاج: {movie['year']}\n"
        f"🎭 التصنيف: {movie['genres']}\n\n"
        f"📝 قصة الفيلم:\n"
        f"{movie['overview']}"
    )
    try:
        if movie['poster']:
            bot.send_photo(CHANNEL_ID, movie['poster'], caption=caption, parse_mode='Markdown')
        else:
            bot.send_message(CHANNEL_ID, caption, parse_mode='Markdown')
        bot.reply_to(message, "✅ تم النشر بنجاح!")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء النشر: {e}")

bot.infinity_polling()
