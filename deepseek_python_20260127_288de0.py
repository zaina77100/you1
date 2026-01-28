#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏭 المصنع الحقيقي - YouTube Shorts Factory
إصدار: 6.0 | يدوي الكامل - يعمل مباشرة مع المفاتيح
تم إضافة جميع الميزات المطلوبة مع التعديلات الفنية
"""

import os
import sys
import json
import time
import random
import shutil
import tempfile
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# ==================== 🔧 الإعدادات اليدوية - ضع مفاتيحك هنا ====================
class FactoryConfig:
    """إعدادات المصنع - جميع المتغيرات يدوية"""
    
    # 🔐 المفاتيح اليدوية - ضع قيمك هنا مباشرة
    YOUTUBE_CLIENT_ID = "629211364418-rl4el36j96go6qvu5ge7n3nac3mqaaad.apps.googleusercontent.com"
    YOUTUBE_CLIENT_SECRET = "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"
    YOUTUBE_REFRESH_TOKEN = "1//04gTjMFbw7M6ACgYIARAAGAQSNwF-L9IreiH8ylSyVxsfSGOcmTppbQzJmNOP-ohHhtTQN2TZrzZ0nKHE9g_B-bj90nN6AHq3IJM"
    
    # 🔑 مفتاح Gemini API
    GEMINI_API_KEY = "AIzaSyDpSepq6kZYj3gQFzIN0xsGbbgH8Hv6xaA"
    
    # 🔢 إعدادات الحساب - ضع رقم حسابك هنا (1, 2, 3, إلخ)
    ACCOUNT_NUMBER = 1  # غيّر هذا الرقم لكل حساب
    
    # ⏰ حساب وقت البدء بناءً على رقم الحساب (توزيع على 24 ساعة)
    # الحساب 1 يبدأ الساعة 8 صباحاً، الحساب 2 الساعة 4 عصراً، إلخ
    START_HOUR = (8 + (ACCOUNT_NUMBER - 1) * 8) % 24
    
    # 📊 إعدادات القناة
    CHANNEL_NAME = f"Tech Shorts {ACCOUNT_NUMBER}"
    DAILY_TARGET = 3  # عدد الفيديوهات اليومي
    VIDEO_DURATION = 60  # مدة الشورت بالثواني
    
    # 🎬 إعدادات المونتاج
    TARGET_RESOLUTION = (1080, 1920)  # أبعاد الشورت
    
    # ⏰ إعدادات الجدولة
    BASE_INTERVAL = 7200  # 2 ساعة بين الفيديوهات
    VARIATION = 600  # تغيير عشوائي 10 دقائق
    
    # 🎯 مواضيع الفيديوهات
    ENGLISH_TOPICS = [
        "AI Technology", "Crypto Secrets", "Business Growth",
        "Wealth Building", "Tech Gadgets", "Future Predictions",
        "Money Making", "Success Habits", "Digital Marketing",
        "Startup Tips", "Investment Strategies", "Productivity Hacks",
        "Mindset Mastery", "Passive Income", "Stock Market",
        "Real Estate Investing", "E-commerce", "Social Media Growth",
        "Personal Finance", "Online Business", "NFT Investments",
        "Metaverse Opportunities", "Web3 Technology", "AI Revolution"
    ]
    
    # 📁 مسارات النظام
    BASE_DIR = Path(".").resolve()
    TEMP_DIR = BASE_DIR / "temp"
    LOGS_DIR = BASE_DIR / "logs"
    COOKIES_FILE = BASE_DIR / "cookies.txt"
    
    @classmethod
    def setup_directories(cls):
        """إنشاء مجلدات النظام"""
        for directory in [cls.TEMP_DIR, cls.LOGS_DIR]:
            directory.mkdir(exist_ok=True)
        
        print(f"""
        ⚙️  إعدادات الحساب #{cls.ACCOUNT_NUMBER}:
        • وقت البدء: {cls.START_HOUR}:00
        • الهدف اليومي: {cls.DAILY_TARGET} شورتس
        • التوكن: {'✅' if cls.YOUTUBE_REFRESH_TOKEN else '❌'}
        • AI: {'✅' if cls.GEMINI_API_KEY else '❌'}
        """)

# ==================== 🔑 نظام تجديد التوكن التلقائي ====================
class TokenManager:
    """إدارة وتجديد الـ Access Tokens تلقائياً"""
    
    def __init__(self):
        self.access_token = None
        self.token_expiry = None
        print("🔑 Token Manager: مهيأ")
    
    def refresh_access_token(self):
        """تجديد الـ Access Token تلقائياً - تعمل عند كل تشغيل"""
        try:
            import requests
            
            print("🔄 جاري تجديد الـ Access Token تلقائياً...")
            
            url = "https://oauth2.googleapis.com/token"
            data = {
                'client_id': FactoryConfig.YOUTUBE_CLIENT_ID,
                'client_secret': FactoryConfig.YOUTUBE_CLIENT_SECRET,
                'refresh_token': FactoryConfig.YOUTUBE_REFRESH_TOKEN,
                'grant_type': 'refresh_token'
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.post(url, data=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens['access_token']
                # ينتهي التوكن بعد 3599 ثانية (~1 ساعة)
                self.token_expiry = datetime.now() + timedelta(seconds=3500)
                
                print(f"✅ تم تجديد الـ Access Token بنجاح")
                print(f"📅 ينتهي في: {self.token_expiry.strftime('%H:%M:%S')}")
                return self.access_token
            else:
                print(f"❌ فشل تجديد Token: {response.status_code}")
                if response.status_code == 400:
                    print("⚠️ قد يكون الـ Refresh Token منتهي الصلاحية")
                print(f"📝 التفاصيل: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ خطأ في تجديد Token: {e}")
            return None
    
    def get_valid_token(self):
        """الحصول على token صالح - يجدد تلقائياً إذا منتهي"""
        # دائماً نجدد عند التشغيل للتأكد من الصلاحية
        if not self.access_token:
            return self.refresh_access_token()
        
        # إذا كان التوكن منتهي الصلاحية، نجدد
        if self.token_expiry and datetime.now() > self.token_expiry:
            print("⏰ الـ Access Token منتهي الصلاحية، جاري التجديد...")
            return self.refresh_access_token()
        
        return self.access_token

# ==================== 🎬 محرك المونتاج مع FFmpeg ====================
class VideoEditEngine:
    """محرك مونتاج متقدم مع FFmpeg"""
    
    def __init__(self):
        self.ffmpeg_installed = self.check_ffmpeg()
    
    def check_ffmpeg(self):
        """التحقق من وجود FFmpeg وتثبيته إذا لزم"""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                          capture_output=True, text=True, check=True)
            print("✅ FFmpeg مثبت")
            return True
        except:
            print("⚠️ FFmpeg غير مثبت - جاري التثبيت التلقائي...")
            try:
                # تثبيت FFmpeg على أنظمة مختلفة
                import platform
                system = platform.system()
                
                if system == "Windows":
                    # على Windows يمكن تحميله تلقائياً
                    print("📦 جاري تحميل FFmpeg لـ Windows...")
                    # سيتم استخدام نسخة محمولة
                elif system == "Linux":
                    subprocess.run(['sudo', 'apt-get', 'update'], check=False)
                    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'ffmpeg'], check=False)
                    print("✅ FFmpeg مثبت على Linux")
                elif system == "Darwin":  # macOS
                    subprocess.run(['brew', 'install', 'ffmpeg'], check=False)
                    print("✅ FFmpeg مثبت على macOS")
                
                # التحقق مرة أخرى
                subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, check=True)
                return True
            except:
                print("❌ لا يمكن تثبيت FFmpeg تلقائياً")
                return False
    
    def download_source_video(self, keyword):
        """تحميل فيديو مصدر مع تجاوز حظر يوتيوب"""
        try:
            import yt_dlp
            
            # إعدادات متقدمة لمحاكاة المتصفح الحقيقي
            ydl_opts = {
                'format': 'best[height<=720][filesize<100M]',
                'outtmpl': str(FactoryConfig.TEMP_DIR / '%(id)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
                
                # ⚡ إعدادات محاكاة المتصفح لتجنب 403
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'http_headers': {
                    'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                    'Referer': 'https://www.youtube.com/',
                    'Origin': 'https://www.youtube.com',
                },
                
                # إعدادات تجنب الحظر
                'socket_timeout': 60,
                'retries': 20,
                'fragment_retries': 15,
                'skip_unavailable_fragments': True,
                'ignoreerrors': True,
                'no_check_certificate': True,
                'prefer_ffmpeg': True,
                'geo_bypass': True,
                'geo_bypass_country': 'US',
                'throttled_rate': '2M',
                'buffersize': '1024k',
                'http_chunk_size': '1048576',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                        'player_skip': ['configs', 'webpage'],
                        'skip': ['hls', 'dash'],
                        'format_sort': ['res:720', 'ext:mp4'],
                    }
                },
                'postprocessor_args': {
                    'sponsorblock': ['--remove', 'sponsor'],
                },
                'concurrent_fragment_downloads': 3,
                'limit_rate': '5M',
                'verbose': True,
            }
            
            # استخدام الكوكيز إذا كان الملف موجوداً
            if FactoryConfig.COOKIES_FILE.exists():
                ydl_opts['cookiefile'] = str(FactoryConfig.COOKIES_FILE)
                print("🍪 استخدام ملف الكوكيز للتحميل")
            
            print(f"🔍 جاري البحث والتحميل عن: {keyword}")
            print("🌐 استخدام إعدادات متصفح متقدمة لتجنب الحظر...")
            
            url = f"ytsearch10:{keyword} shorts"  # البحث عن شورتات
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=True)
                    
                    if 'entries' in info:
                        # اختيار فيديو عشوائي من النتائج
                        videos = [v for v in info['entries'] if v]
                        if videos:
                            video = random.choice(videos)
                        else:
                            raise Exception("لا توجد فيديوهات متاحة")
                    else:
                        video = info
                    
                    video_path = FactoryConfig.TEMP_DIR / f"{video['id']}.{video['ext']}"
                    
                    if video_path.exists():
                        print(f"✅ تم تحميل الفيديو بنجاح:")
                        print(f"   📝 العنوان: {video.get('title', 'Unknown')[:60]}...")
                        print(f"   ⏱️  المدة: {video.get('duration', 0)} ثانية")
                        print(f"   💾 الحجم: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
                        
                        return video_path, video.get('duration', 60)
                    else:
                        print("❌ الملف غير موجود بعد التحميل")
                        return None, 0
                        
                except Exception as extract_error:
                    print(f"⚠️ خطأ في الاستخراج: {extract_error}")
                    # المحاولة بطريقة بديلة
                    return self._download_backup_method(keyword)
                
        except ImportError:
            print("❌ yt-dlp غير مثبت - جاري التثبيت...")
            subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"])
            return self.download_source_video(keyword)
        except Exception as e:
            print(f"❌ خطأ عام في التحميل: {e}")
            return self._download_backup_method(keyword)
    
    def _download_backup_method(self, keyword):
        """طريقة احتياطية للتحميل"""
        print("🔄 استخدام الطريقة الاحتياطية للتحميل...")
        try:
            # استخدام yt-dlp مباشرة كأمر فرعي
            video_id = f"backup_{int(time.time())}"
            output_path = FactoryConfig.TEMP_DIR / f"{video_id}.mp4"
            
            cmd = [
                'yt-dlp',
                '--format', 'best[height<=720][filesize<50M]',
                '--max-filesize', '50M',
                '--output', str(output_path),
                '--no-playlist',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                '--add-header', 'Accept-Language:en-US,en;q=0.9',
                '--add-header', 'Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                '--add-header', 'Referer:https://www.youtube.com/',
                '--socket-timeout', '60',
                '--retries', '15',
                '--fragment-retries', '10',
                '--skip-unavailable-fragments',
                '--ignore-errors',
                '--no-check-certificate',
                '--geo-bypass',
                '--throttled-rate', '2M',
                '--concurrent-fragments', '2',
                f"ytsearch1:{keyword}"
            ]
            
            print(f"📥 جاري التحميل بالطريقة الاحتياطية...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and output_path.exists():
                print(f"✅ تم التحميل بنجاح بالطريقة الاحتياطية")
                return output_path, 60
            else:
                print(f"❌ فشل التحميل: {result.stderr[:200]}")
                return None, 0
                
        except Exception as e:
            print(f"❌ خطأ في التحميل الاحتياطي: {e}")
            return None, 0
    
    def convert_to_shorts_format(self, source_path, duration):
        """تحويل الفيديو إلى تنسيق YouTube Shorts (1080x1920)"""
        if not self.ffmpeg_installed:
            print("❌ FFmpeg غير متوفر - لا يمكن التحويل")
            return None
        
        try:
            output_path = FactoryConfig.TEMP_DIR / f"shorts_{int(time.time())}.mp4"
            
            # اختيار جزء 60 ثانية من الفيديو
            if duration > 60:
                # اختيار أفضل 60 ثانية (من المنتصف عادةً)
                start_time = max(0, (duration - 60) / 2)
            else:
                start_time = 0
            
            print(f"🎬 جاري تحويل الفيديو إلى تنسيق Shorts (1080x1920)...")
            print(f"   ⏱️  المدة النهائية: 60 ثانية")
            print(f"   📏 الأبعاد: {FactoryConfig.TARGET_RESOLUTION[0]}x{FactoryConfig.TARGET_RESOLUTION[1]}")
            
            # فلتر FFmpeg متقدم لتحويل إلى 9:16 مع الحفاظ على الجودة
            filter_complex = (
                f"scale={FactoryConfig.TARGET_RESOLUTION[0]}:{FactoryConfig.TARGET_RESOLUTION[1]}:"
                f"force_original_aspect_ratio=decrease,"
                f"pad={FactoryConfig.TARGET_RESOLUTION[0]}:{FactoryConfig.TARGET_RESOLUTION[1]}:"
                f"(ow-iw)/2:(oh-ih)/2:color=black,"
                f"setsar=1,fps=30"
            )
            
            cmd = [
                'ffmpeg',
                '-y',  # الكتابة فوق الملفات الموجودة
                '-ss', str(start_time),  # وقت البدء
                '-i', str(source_path),  # ملف الإدخال
                '-t', '60',  # المدة 60 ثانية
                '-vf', filter_complex,  # الفلاتر
                '-c:v', 'libx264',  # كودك الفيديو
                '-preset', 'fast',  # توازن بين السرعة والجودة
                '-crf', '22',  # جودة عالية
                '-profile:v', 'high',
                '-level', '4.0',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',  # كودك الصوت
                '-b:a', '192k',  # جودة صوت عالية
                '-ar', '48000',
                '-ac', '2',
                '-movflags', '+faststart',  # لبدء التشغيل السريع
                '-threads', '0',  # استخدام كل الأنوية
                str(output_path)
            ]
            
            print(f"   🔧 جاري معالجة الفيديو...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                if output_path.exists():
                    file_size = os.path.getsize(output_path) / (1024*1024)
                    print(f"✅ تم تحويل الفيديو بنجاح!")
                    print(f"   💾 الحجم النهائي: {file_size:.1f} MB")
                    print(f"   📍 الموقع: {output_path}")
                    return output_path
                else:
                    print("❌ الملف الناتج غير موجود")
                    return None
            else:
                print(f"❌ خطأ في FFmpeg: {result.stderr[:300]}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ انتهى وقت معالجة الفيديو")
            return None
        except Exception as e:
            print(f"❌ خطأ في تحويل الفيديو: {e}")
            return None
    
    def add_watermark_and_title(self, video_path, title):
        """إضافة علامة مائية وعنوان على الفيديو"""
        try:
            output_path = FactoryConfig.TEMP_DIR / f"final_{video_path.name}"
            
            # تنظيف العنوان للـ FFmpeg
            safe_title = title.replace("'", "'\\''").replace(":", "\\:").replace("%", "%%")
            
            # فلتر معقد لإضافة العنوان والعلامة المائية
            filter_complex = (
                f"drawtext=text='{safe_title}':"
                f"fontcolor=white:fontsize=48:"
                f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"box=1:boxcolor=black@0.6:boxborderw=10:"
                f"x=(w-text_w)/2:y=100:"
                f"enable='between(t,0,5)',"
                f"drawtext=text='© {FactoryConfig.CHANNEL_NAME}':"
                f"fontcolor=white@0.5:fontsize=24:"
                f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
                f"x=w-text_w-20:y=h-text_h-20:"
                f"enable='between(t,0,60)'"
            )
            
            cmd = [
                'ffmpeg',
                '-y',
                '-i', str(video_path),
                '-vf', filter_complex,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'copy',  # نسخ الصوت كما هو
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and output_path.exists():
                print(f"✨ تم إضافة العنوان والعلامة المائية")
                return output_path
            else:
                print(f"⚠️ خطأ في إضافة العلامة المائية، استخدام الفيديو الأصلي")
                return video_path
                
        except Exception as e:
            print(f"⚠️ خطأ في إضافة العلامة المائية: {e}")
            return video_path

# ==================== 🧠 نظام الذكاء الاصطناعي ====================
class AIContentFactory:
    """مصنع المحتوى بالذكاء الاصطناعي"""
    
    def __init__(self):
        self.api_key = FactoryConfig.GEMINI_API_KEY
        self.model = None
        self.setup_gemini()
    
    def setup_gemini(self):
        """تهيئة Gemini AI"""
        if not self.api_key:
            print("⚠️ لا يوجد مفتاح Gemini API - استخدام العناوين الافتراضية")
            return
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini AI جاهز للتوليد")
        except ImportError:
            print("❌ google-generativeai غير مثبت")
        except Exception as e:
            print(f"⚠️ خطأ في Gemini: {e}")
    
    def generate_viral_title(self, topic):
        """توليد عنوان فيروسي"""
        if not self.model:
            return self._fallback_title(topic)
        
        try:
            prompt = f"""Generate ONE viral YouTube Shorts title about: {topic}

Requirements:
1. ONE title only (40-70 characters)
2. Add ONE relevant emoji at the beginning
3. Make it controversial or create curiosity
4. Include power words
5. English only
6. Focus on benefits or secrets

Examples of good titles:
😱 This {topic} SECRET Made Me $10,000
🚀 How I Used {topic} To Quit My Job
⚠️ STOP Using {topic} Until You Watch This
💥 The {topic} Method NOBODY Talks About

Now generate ONE title:"""
            
            response = self.model.generate_content(prompt)
            title = response.text.strip().split('\n')[0].strip()
            
            # تنظيف النتيجة
            title = title.replace('"', '').replace("'", "").strip()
            
            # التأكد من وجود إيموجي
            import emoji
            if not any(char in emoji.EMOJI_DATA for char in title[:2]):
                emojis = ["😱", "🚀", "⚠️", "💥", "🔥", "💰", "📈", "🎯", "⚡", "✨"]
                title = random.choice(emojis) + " " + title
            
            # تقليل الطول إذا كان طويلاً
            if len(title) > 80:
                title = title[:77] + "..."
            
            print(f"🧠 AI Generated Title: {title}")
            return title
            
        except Exception as e:
            print(f"❌ خطأ في توليد العنوان: {e}")
            return self._fallback_title(topic)
    
    def _fallback_title(self, topic):
        """عناوين احتياطية"""
        templates = [
            f"😱 This {topic} Secret Will Make You Rich",
            f"🚀 How to Make $1000 Daily With {topic}",
            f"⚠️ The Truth About {topic} Nobody Tells You",
            f"💥 {topic} Strategy That Made Me $5000",
            f"🔥 STOP Doing {topic} Wrong - Do This Instead",
            f"💰 How I Made $10,000 With {topic}",
            f"📈 The Ultimate {topic} Guide for Beginners",
            f"🎯 {topic} Masterclass: From Zero to Hero",
            f"⚡ {topic} Hacks That Actually Work",
            f"✨ The Secret {topic} Method Revealed"
        ]
        title = random.choice(templates)
        print(f"📝 Fallback Title: {title}")
        return title
    
    def generate_description(self, title, topic):
        """توليد وصف الفيديو مع الهاشتاقات"""
        # إنشاء هاشتاقات ذكية
        base_hashtags = [
            "shorts", "viral", "money", "success", "business",
            "tech", "entrepreneur", "motivation", "tips", "hack"
        ]
        
        topic_hashtags = [
            topic.lower().replace(" ", ""),
            topic.replace(" ", ""),
            topic.lower().replace(" ", "_"),
            "ai" if "ai" in topic.lower() else "",
            "crypto" if "crypto" in topic.lower() else "",
            "investing" if any(word in topic.lower() for word in ["money", "wealth", "invest"]) else ""
        ]
        
        # فلترة الهاشتاقات الفارغة
        topic_hashtags = [tag for tag in topic_hashtags if tag]
        
        # دمج وخلط الهاشتاقات
        all_hashtags = topic_hashtags + base_hashtags
        random.shuffle(all_hashtags)
        
        # اختيار 12 هاشتاق كحد أقصى
        selected_hashtags = all_hashtags[:12]
        
        description = f"""{title}

📌 What you'll learn in this Short:
• The secret behind {topic}
• How to apply this in real life
• Step-by-step guide

🔔 Don't forget to SUBSCRIBE for daily content!

👇 Follow for more:
#{" #".join(selected_hashtags)}

⚠️ Disclaimer: This is educational content. Always do your own research.
"""
        
        return description.strip()
    
    def generate_tags(self, topic, title):
        """توليد tags للفيديو"""
        words = title.lower().split() + topic.lower().split()
        
        # إزالة الكلمات الشائعة
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = [word for word in words if word not in common_words and len(word) > 2]
        
        # إضافة كلمات مفتاحية
        keywords = [
            "shorts", "short", "youtubeshorts", "viralshorts",
            "moneyshorts", "success", "motivation",
            "howto", "tutorial", "tips", "hacks"
        ]
        
        tags = list(set(words + keywords))[:25]  # YouTube allows up to 500 characters
        
        return tags

# ==================== 📤 نظام الرفع الحقيقي ====================
class YouTubeUploader:
    """نظام الرفع الحقيقي باستخدام YouTube API"""
    
    def __init__(self):
        self.token_manager = TokenManager()
        print("✅ YouTube Uploader جاهز للرفع الحقيقي")
    
    def upload_video(self, video_path, title, description, tags):
        """رفع فيديو حقيقي لليوتيوب"""
        try:
            # الحصول على token صالح (سيجدد تلقائياً إذا لزم)
            access_token = self.token_manager.get_valid_token()
            if not access_token:
                print("❌ لا يمكن الحصول على Access Token صالح")
                print("⚠️ تحقق من الـ Refresh Token والمفاتيح")
                return None
            
            print(f"🚀 بدء الرفع الحقيقي لليوتيوب:")
            print(f"   📝 العنوان: {title[:50]}...")
            print(f"   📁 الملف: {video_path.name}")
            print(f"   📏 الحجم: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
            
            # الرفع باستخدام YouTube Data API v3
            result = self._upload_with_youtube_api(video_path, title, description, tags, access_token)
            
            if result:
                print(f"✅ تم الرفع بنجاح!")
                return result
            else:
                print("❌ فشل الرفع")
                return None
                
        except Exception as e:
            print(f"❌ خطأ في عملية الرفع: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _upload_with_youtube_api(self, video_path, title, description, tags, access_token):
        """الرفع الحقيقي باستخدام YouTube API"""
        try:
            import requests
            
            # ===== 1. إعداد البيانات =====
            video_metadata = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": "22",  # People & Blogs
                    "defaultLanguage": "en",
                    "defaultAudioLanguage": "en"
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                    "embeddable": True,
                    "license": "youtube",
                    "publicStatsViewable": True
                }
            }
            
            # ===== 2. إنشاء جلسة الرفع =====
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=utf-8",
                "X-Upload-Content-Length": str(os.path.getsize(video_path)),
                "X-Upload-Content-Type": "video/*"
            }
            
            upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"
            params = {
                "part": "snippet,status",
                "uploadType": "resumable"  # للنقل المستمر للفيديوهات الكبيرة
            }
            
            print("📤 جاري إنشاء جلسة الرفع...")
            session_response = requests.post(
                upload_url,
                headers=headers,
                params=params,
                json=video_metadata,
                timeout=30
            )
            
            if session_response.status_code != 200:
                print(f"❌ فشل إنشاء جلسة الرفع: {session_response.status_code}")
                print(f"📝 الاستجابة: {session_response.text[:200]}")
                return None
            
            upload_location = session_response.headers.get("Location")
            if not upload_location:
                print("❌ لا يوجد رابط للرفع في الاستجابة")
                return None
            
            print("✅ جلسة الرفع جاهزة")
            
            # ===== 3. رفع ملف الفيديو =====
            print("📤 جاري رفع ملف الفيديو...")
            
            with open(video_path, 'rb') as video_file:
                upload_headers = {
                    "Content-Type": "video/*",
                    "Content-Length": str(os.path.getsize(video_path))
                }
                
                upload_response = requests.put(
                    upload_location,
                    headers=upload_headers,
                    data=video_file,
                    timeout=300  # 5 دقائق للرفع
                )
            
            if upload_response.status_code in [200, 201]:
                video_info = upload_response.json()
                video_id = video_info.get("id")
                
                if video_id:
                    print(f"🎉 تم الرفع بنجاح!")
                    print(f"   🆔 Video ID: {video_id}")
                    print(f"   🔗 الرابط: https://youtube.com/shorts/{video_id}")
                    print(f"   🔗 الرابط المختصر: https://youtu.be/{video_id}")
                    
                    return {
                        'id': video_id,
                        'title': title,
                        'url': f'https://youtube.com/shorts/{video_id}',
                        'real': True,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    print("❌ لا يوجد ID في الاستجابة")
                    return None
            else:
                print(f"❌ فشل الرفع: {upload_response.status_code}")
                print(f"📝 التفاصيل: {upload_response.text[:300]}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ انتهى وقت الرفع - الفيديو كبير جداً")
            return None
        except Exception as e:
            print(f"❌ خطأ في YouTube API: {e}")
            return None

# ==================== 💾 نظام حفظ الحالة ====================
class StateManager:
    """إدارة حالة النظام"""
    
    def __init__(self):
        self.state_file = FactoryConfig.LOGS_DIR / f"uploads_account_{FactoryConfig.ACCOUNT_NUMBER}.json"
        self.uploaded_videos = self.load_state()
    
    def load_state(self):
        """تحميل الحالة السابقة"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"📖 تم تحميل {len(data)} فيديو من السجل")
                    return data
            except Exception as e:
                print(f"⚠️ خطأ في تحميل السجل: {e}")
                return []
        else:
            print("📝 إنشاء سجل جديد")
            return []
    
    def save_state(self):
        """حفظ الحالة الحالية"""
        try:
            # حفظ آخر 100 فيديو فقط
            to_save = self.uploaded_videos[-100:] if len(self.uploaded_videos) > 100 else self.uploaded_videos
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(to_save, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"💾 تم حفظ {len(to_save)} فيديو في السجل")
            return True
        except Exception as e:
            print(f"❌ خطأ في حفظ السجل: {e}")
            return False
    
    def add_uploaded_video(self, video_data):
        """إضافة فيديو جديد إلى السجل"""
        video_record = {
            'id': video_data.get('id'),
            'title': video_data.get('title'),
            'url': video_data.get('url'),
            'timestamp': datetime.now().isoformat(),
            'account': FactoryConfig.ACCOUNT_NUMBER,
            'channel': FactoryConfig.CHANNEL_NAME
        }
        
        self.uploaded_videos.append(video_record)
        self.save_state()
        print(f"📝 تم تسجيل الفيديو في السجل")
    
    def get_today_uploads(self):
        """الحصول على عدد الرفعات اليوم"""
        today = datetime.now().date()
        today_uploads = []
        
        for video in self.uploaded_videos:
            try:
                video_date = datetime.fromisoformat(video['timestamp']).date()
                if video_date == today:
                    today_uploads.append(video)
            except:
                continue
        
        print(f"📊 اليوم: {len(today_uploads)}/{FactoryConfig.DAILY_TARGET}")
        return len(today_uploads)

# ==================== ⏰ نظام الجدولة الذكي ====================
class SmartScheduler:
    """نظام جدولة ذكي مع توزيع الحسابات"""
    
    def __init__(self):
        self.account_number = FactoryConfig.ACCOUNT_NUMBER
        self.start_hour = FactoryConfig.START_HOUR
        self.wait_for_start_time()
    
    def wait_for_start_time(self):
        """الانتظار حتى وقت البدء المخصص"""
        now = datetime.now()
        
        # حساب وقت البدء
        target_time = now.replace(
            hour=self.start_hour,
            minute=0,
            second=0,
            microsecond=0
        )
        
        # إذا كان وقت البدء قد مضى اليوم، ننتظر حتى الغد
        if target_time < now:
            target_time += timedelta(days=1)
        
        wait_seconds = (target_time - now).total_seconds()
        
        if wait_seconds > 0:
            wait_hours = int(wait_seconds // 3600)
            wait_minutes = int((wait_seconds % 3600) // 60)
            
            print(f"\n⏰ جدولة الحساب #{self.account_number}:")
            print(f"   • وقت البدء: {self.start_hour:02d}:00")
            print(f"   • الوقت الحالي: {now.strftime('%H:%M:%S')}")
            print(f"   • الانتظار: {wait_hours} ساعة {wait_minutes} دقيقة")
            
            if wait_seconds > 3600:  # أكثر من ساعة
                # إظهار العداد كل ساعة
                for hour in range(wait_hours, 0, -1):
                    if hour <= 6:  # آخر 6 ساعات فقط
                        print(f"   ⏳ باقي {hour} ساعة...")
                    time.sleep(3600)
                
                # الدقائق المتبقية
                if wait_minutes > 0:
                    print(f"   ⏳ باقي {wait_minutes} دقيقة...")
                    time.sleep(wait_minutes * 60)
            else:
                # أقل من ساعة: إظهار العداد كل 10 دقائق
                for minute in range(int(wait_seconds // 60), 0, -10):
                    if minute <= 30:  # آخر 30 دقيقة
                        print(f"   ⏳ باقي {minute} دقيقة...")
                    time.sleep(min(600, minute * 60))
            
            print(f"\n🚀 بدء الحساب #{self.account_number} في {self.start_hour:02d}:00")
        else:
            print(f"🚀 بدء الحساب #{self.account_number} الآن")
    
    def calculate_next_upload(self):
        """حساب وقت الرفع التالي"""
        # تغيير عشوائي في الفترة
        variation = random.randint(-FactoryConfig.VARIATION, FactoryConfig.VARIATION)
        interval = FactoryConfig.BASE_INTERVAL + variation
        
        # تحويل إلى ساعات ودقائق
        hours = interval // 3600
        minutes = (interval % 3600) // 60
        
        if hours > 0:
            wait_text = f"{hours} ساعة {minutes} دقيقة"
        else:
            wait_text = f"{minutes} دقيقة"
        
        next_time = datetime.now() + timedelta(seconds=interval)
        
        print(f"\n⏰ وقت الرفع التالي:")
        print(f"   • بعد: {wait_text}")
        print(f"   • الساعة: {next_time.strftime('%H:%M:%S')}")
        
        return interval

# ==================== 🏭 المصنع الرئيسي ====================
class YouTubeShortsFactory:
    """المصنع الرئيسي الكامل"""
    
    def __init__(self):
        # إعداد النظام
        FactoryConfig.setup_directories()
        
        # تهيئة الأنظمة
        self.video_engine = VideoEditEngine()
        self.ai_factory = AIContentFactory()
        self.uploader = YouTubeUploader()
        self.state_manager = StateManager()
        self.scheduler = SmartScheduler()
        
        # الإحصائيات
        self.stats = {
            'account': FactoryConfig.ACCOUNT_NUMBER,
            'start_time': datetime.now(),
            'total_produced': 0,
            'real_uploads': 0,
            'failed_attempts': 0,
            'daily_target': FactoryConfig.DAILY_TARGET
        }
        
        self.display_banner()
    
    def display_banner(self):
        """عرض بانر المصنع"""
        banner = f"""
        {'='*70}
        🏭   YouTube Shorts Factory v6.0   🏭
        {'='*70}
        
        ⚙️  الإعدادات النشطة:
        • الحساب النشط: #{FactoryConfig.ACCOUNT_NUMBER}
        • اسم القناة: {FactoryConfig.CHANNEL_NAME}
        • وقت البدء: {FactoryConfig.START_HOUR:02d}:00
        • الهدف اليومي: {FactoryConfig.DAILY_TARGET} شورتس
        • الفترة بين الرفعات: {FactoryConfig.BASE_INTERVAL//3600} ساعة
        
        📊 حالة النظام:
        • Refresh Token: {'✅ جاهز' if FactoryConfig.YOUTUBE_REFRESH_TOKEN else '❌ مفقود'}
        • Gemini AI: {'✅ مفعل' if FactoryConfig.GEMINI_API_KEY else '❌ غير مفعل'}
        • FFmpeg: {'✅ مثبت' if self.video_engine.ffmpeg_installed else '❌ غير مثبت'}
        
        ⏰ وقت التشغيل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        {'='*70}
        """
        print(banner)
    
    def produce_single_shorts(self, production_number):
        """إنتاج شورت واحد كامل"""
        print(f"\n🎬 جولة الإنتاج #{production_number}")
        print("-"*60)
        
        try:
            # ===== 1. اختيار الموضوع =====
            topic = random.choice(FactoryConfig.ENGLISH_TOPICS)
            print(f"📌 الموضوع المختار: {topic}")
            
            # ===== 2. توليد المحتوى =====
            print("🧠 جاري توليد المحتوى...")
            title = self.ai_factory.generate_viral_title(topic)
            description = self.ai_factory.generate_description(title, topic)
            tags = self.ai_factory.generate_tags(topic, title)
            
            print(f"📝 العنوان: {title}")
            
            # ===== 3. تحميل الفيديو المصدر =====
            print("\n📥 جاري البحث عن فيديو مصدر...")
            source_path, duration = self.video_engine.download_source_video(topic)
            
            if not source_path or not source_path.exists():
                print("❌ فشل تحميل الفيديو المصدر")
                self.stats['failed_attempts'] += 1
                return False
            
            print(f"✅ تم تحميل الفيديو: {source_path.name}")
            
            # ===== 4. تحويل إلى تنسيق Shorts =====
            print("\n🎬 جاري تحويل إلى تنسيق YouTube Shorts...")
            shorts_path = self.video_engine.convert_to_shorts_format(source_path, duration)
            
            if not shorts_path or not shorts_path.exists():
                print("❌ فشل تحويل الفيديو")
                self.cleanup_temp_files([source_path])
                return False
            
            # ===== 5. إضافة العنوان والعلامة المائية =====
            print("\n✨ جاري إضافة العنوان والعلامة المائية...")
            final_video = self.video_engine.add_watermark_and_title(shorts_path, title)
            
            if not final_video.exists():
                print("⚠️ استخدام الفيديو بدون علامة مائية")
                final_video = shorts_path
            
            # ===== 6. الرفع إلى YouTube =====
            print("\n🚀 بدء الرفع إلى YouTube...")
            upload_result = self.uploader.upload_video(final_video, title, description, tags)
            
            # ===== 7. التنظيف =====
            self.cleanup_temp_files([source_path, shorts_path, final_video])
            
            # ===== 8. حفظ النتيجة =====
            if upload_result and upload_result.get('real'):
                self.stats['total_produced'] += 1
                self.stats['real_uploads'] += 1
                self.state_manager.add_uploaded_video(upload_result)
                
                print(f"\n✅ اكتملت الجولة #{production_number} بنجاح!")
                print(f"   🆔 Video ID: {upload_result.get('id')}")
                print(f"   🔗 الرابط: {upload_result.get('url')}")
                
                return True
            else:
                print(f"\n❌ فشلت جولة الإنتاج #{production_number}")
                self.stats['failed_attempts'] += 1
                return False
                
        except Exception as e:
            print(f"\n💥 خطأ غير متوقع في الإنتاج: {e}")
            import traceback
            traceback.print_exc()
            self.stats['failed_attempts'] += 1
            return False
    
    def cleanup_temp_files(self, files):
        """تنظيف الملفات المؤقتة"""
        print("🧹 جاري تنظيف الملفات المؤقتة...")
        cleaned = 0
        
        for file_path in files:
            if file_path and isinstance(file_path, Path) and file_path.exists():
                try:
                    file_path.unlink()
                    cleaned += 1
                except Exception as e:
                    print(f"⚠️ لا يمكن حذف {file_path.name}: {e}")
        
        print(f"✅ تم تنظيف {cleaned} ملف")
    
    def run_daily_production(self):
        """تشغيل دورة الإنتاج اليومية"""
        print(f"\n🏭 بدء دورة الإنتاج اليومية للحساب #{self.stats['account']}")
        print(f"🎯 الهدف: {self.stats['daily_target']} شورتس")
        print("="*60)
        
        produced_today = 0
        max_attempts = self.stats['daily_target'] * 3  # حد أقصى للمحاولات
        
        try:
            while produced_today < self.stats['daily_target']:
                # التحقق من الرفعات اليومية
                today_uploads = self.state_manager.get_today_uploads()
                if today_uploads >= self.stats['daily_target']:
                    print(f"\n🎯 تم تحقيق الهدف اليومي: {today_uploads} شورتس")
                    break
                
                # التحقق من عدد المحاولات الفاشلة
                if self.stats['failed_attempts'] >= 5:
                    print(f"\n🚨 كثرة الأخطاء ({self.stats['failed_attempts']})، توقف مؤقت لمدة 10 دقائق")
                    time.sleep(600)
                    self.stats['failed_attempts'] = 0
                
                # إنتاج شورت
                attempt_number = produced_today + 1
                success = self.produce_single_shorts(attempt_number)
                
                if success:
                    produced_today += 1
                    
                    # عرض الإحصائيات
                    print(f"\n📊 الإحصائيات الحالية:")
                    print(f"   • المنتج اليوم: {produced_today}/{self.stats['daily_target']}")
                    print(f"   • الإجمالي: {self.stats['total_produced']}")
                    print(f"   • الرفع الحقيقي: {self.stats['real_uploads']}")
                    
                    # إذا لم نصل للهدف، ننتظر للجولة التالية
                    if produced_today < self.stats['daily_target']:
                        wait_time = self.scheduler.calculate_next_upload()
                        print(f"\n😴 انتظار الجولة التالية...")
                        
                        # انتظار مع عداد
                        self.countdown_timer(wait_time)
                        
                        print("\n" + "="*60)
                else:
                    print(f"⚠️ محاولة فاشلة، إعادة المحاولة بعد دقيقتين...")
                    time.sleep(120)
                
                # التحقق من الحد الأقصى للمحاولات
                total_attempts = produced_today + self.stats['failed_attempts']
                if total_attempts >= max_attempts:
                    print(f"\n🚨 وصلت للحد الأقصى للمحاولات ({max_attempts})")
                    break
            
        except KeyboardInterrupt:
            print("\n\n🛑 تم إيقاف الإنتاج يدوياً")
        except Exception as e:
            print(f"\n💥 خطأ جسيم في دورة الإنتاج: {e}")
        
        # عرض التقرير النهائي
        self.show_final_report(produced_today)
    
    def countdown_timer(self, seconds):
        """عداد تنازلي مع تحديثات"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining_seconds = int(seconds % 60)
        
        total_minutes = int(seconds // 60)
        
        # إظهار تحديثات كل 5 دقائق (أو أقل إذا كانت المدة قصيرة)
        update_interval = 300 if total_minutes > 10 else 60
        
        for remaining in range(int(seconds), 0, -update_interval):
            current_hours = remaining // 3600
            current_minutes = (remaining % 3600) // 60
            
            if current_hours > 0:
                print(f"   ⏳ باقي {current_hours} ساعة {current_minutes} دقيقة...")
            else:
                print(f"   ⏳ باقي {current_minutes} دقيقة...")
            
            time.sleep(min(update_interval, remaining))
        
        print("   ✅ وقت الانتظار انتهى!")
    
    def show_final_report(self, produced_count):
        """عرض التقرير النهائي"""
        elapsed = datetime.now() - self.stats['start_time']
        hours = elapsed.total_seconds() / 3600
        
        print("\n" + "="*70)
        print("📊 تقرير الإنتاج النهائي")
        print("="*70)
        
        print(f"🏭 المصنع: #{self.stats['account']}")
        print(f"⏱️  وقت التشغيل: {hours:.2f} ساعة")
        print(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*40)
        print(f"🎬 الشورتات المنتجة اليوم: {produced_count}")
        print(f"✅ الرفع الحقيقي: {self.stats['real_uploads']}")
        print(f"❌ المحاولات الفاشلة: {self.stats['failed_attempts']}")
        print(f"🎯 الهدف اليومي: {self.stats['daily_target']}")
        
        # حساب الأرباح التقريبية
        if self.stats['real_uploads'] > 0:
            # تقدير تقريبي: كل 1000 مشاهدة ≈ $3-5
            # افتراض أن كل شورت يحصل على 5000 مشاهدة في اليوم الأول
            estimated_views = self.stats['real_uploads'] * 5000
            estimated_earnings = (estimated_views / 1000) * 4  # $4 لكل 1000 مشاهدة
            
            daily_earnings = estimated_earnings
            monthly_earnings = daily_earnings * 30
            
            print(f"\n💰 الأرباح المتوقعة (تقديرية):")
            print(f"   • المشاهدات اليومية: {estimated_views:,}")
            print(f"   • الأرباح اليومية: ${daily_earnings:.2f}")
            print(f"   • الأرباح الشهرية: ${monthly_earnings:.2f}")
            print(f"   ⚠️  ملاحظة: هذه تقديرات وقد تختلف في الواقع")
        
        print(f"\n📁 سجل الرفعات: {self.state_manager.state_file}")
        print("="*70)
        
        # حفظ التقرير في ملف
        self.save_report_to_file(produced_count, hours)
    
    def save_report_to_file(self, produced_count, hours):
        """حفظ التقرير في ملف"""
        report_file = FactoryConfig.LOGS_DIR / f"report_account_{self.stats['account']}_{datetime.now().strftime('%Y%m%d')}.txt"
        
        report_content = f"""YouTube Shorts Factory - Daily Report
===============================
Account: #{self.stats['account']}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Runtime: {hours:.2f} hours

Production Statistics:
• Shorts Produced: {produced_count}
• Real Uploads: {self.stats['real_uploads']}
• Failed Attempts: {self.stats['failed_attempts']}
• Daily Target: {self.stats['daily_target']}

Estimated Earnings:
• Daily Views: {self.stats['real_uploads'] * 5000:,}
• Daily Earnings: ${(self.stats['real_uploads'] * 5000 / 1000) * 4:.2f}
• Monthly Earnings: ${(self.stats['real_uploads'] * 5000 / 1000) * 4 * 30:.2f}

Note: Earnings are estimates based on average YouTube CPM.
"""
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"📄 التقرير محفوظ في: {report_file}")
        except Exception as e:
            print(f"⚠️ لا يمكن حفظ التقرير: {e}")

# ==================== 🚀 نقطة التشغيل الرئيسية ====================
def setup_environment():
    """إعداد بيئة التشغيل التلقائية"""
    print("\n🔧 جاري إعداد بيئة المصنع...")
    
    # المكتبات المطلوبة
    required_libraries = [
        "yt-dlp",
        "google-generativeai",
        "requests",
        "emoji"
    ]
    
    print("📦 تثبيت المكتبات المطلوبة...")
    
    for lib in required_libraries:
        try:
            # تحويل اسم المكتبة للاستيراد
            import_name = lib.replace("-", "_")
            __import__(import_name)
            print(f"   ✅ {lib} مثبت")
        except ImportError:
            print(f"   📦 تثبيت {lib}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])
                print(f"   ✅ تم تثبيت {lib}")
            except:
                print(f"   ❌ فشل تثبيت {lib}")
    
    # التحقق من المفاتيح
    print("\n🔑 التحقق من المفاتيح:")
    if FactoryConfig.YOUTUBE_REFRESH_TOKEN:
        print("   ✅ Refresh Token موجود")
    else:
        print("   ❌ Refresh Token مفقود - الرفع الحقيقي لن يعمل")
    
    if FactoryConfig.GEMINI_API_KEY:
        print("   ✅ Gemini API Key موجود")
    else:
        print("   ⚠️  Gemini API Key مفقود - استخدام العناوين الافتراضية")
    
    print("✅ اكتمل إعداد البيئة")

def main():
    """الدالة الرئيسية للتشغيل"""
    print("\n" + "="*70)
    print("🏭 YouTube Shorts Money Factory v6.0")
    print("🔧 النسخة اليدوية - يعمل مباشرة بالمفاتيح")
    print("="*70)
    
    # التحقق من المتغيرات الأساسية
    if not FactoryConfig.YOUTUBE_CLIENT_ID:
        print("❌ YOUTUBE_CLIENT_ID غير موجود - الرجاء تعبئته في FactoryConfig")
        return
    
    if not FactoryConfig.YOUTUBE_CLIENT_SECRET:
        print("❌ YOUTUBE_CLIENT_SECRET غير موجود - الرجاء تعبئته في FactoryConfig")
        return
    
    if not FactoryConfig.YOUTUBE_REFRESH_TOKEN:
        print("⚠️  YOUTUBE_REFRESH_TOKEN غير موجود - الرفع الحقيقي لن يعمل")
        print("ℹ️  يمكنك الحصول على refresh token من: https://developers.google.com/oauthplayground")
    
    # إعداد البيئة
    setup_environment()
    
    # إنشاء وتشغيل المصنع
    print("\n" + "="*70)
    print("🚀 بدء تشغيل المصنع...")
    
    factory = YouTubeShortsFactory()
    factory.run_daily_production()
    
    print("\n🏭 انتهت الدورة اليومية للمصنع")
    print("="*70)

# ==================== التشغيل التلقائي ====================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 تم إيقاف البرنامج بواسطة المستخدم")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 خطأ جسيم: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
