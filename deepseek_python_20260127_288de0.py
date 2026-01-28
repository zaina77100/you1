#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏭 المصنع الحقيقي - YouTube Shorts Factory
إصدار: 5.0 | متوافق مع GitHub Actions
تم إضافة جميع التعديلات الفنية المطلوبة
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

# ==================== 🔧 إعدادات النظام ====================
class FactoryConfig:
    """إعدادات المصنع - جميع المتغيرات من GitHub Secrets"""
    
    # ⚙️ إعدادات الحسابات (تغيير لكل نسخة)
    ACCOUNT_NUMBER = int(os.getenv("ACCOUNT_NUMBER", "1"))
    START_HOUR = int(os.getenv("START_HOUR", "8"))
    
    # 🔐 المفاتيح السرية من GitHub Secrets
    YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
    YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
    YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # 📊 إعدادات القناة
    CHANNEL_NAME = f"Tech Shorts {ACCOUNT_NUMBER}"
    DAILY_TARGET = int(os.getenv("DAILY_TARGET", "3"))
    VIDEO_DURATION = 60
    
    # 🎬 إعدادات المونتاج
    TARGET_RESOLUTION = (1080, 1920)
    
    # ⏰ إعدادات الجدولة
    BASE_INTERVAL = int(os.getenv("BASE_INTERVAL", "7200"))
    VARIATION = 600
    
    # 🎯 مواضيع الفيديوهات
    ENGLISH_TOPICS = [
        "AI Technology", "Crypto Secrets", "Business Growth",
        "Wealth Building", "Tech Gadgets", "Future Predictions",
        "Money Making", "Success Habits", "Digital Marketing"
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
        
        # التحقق من الملفات المطلوبة
        if not cls.COOKIES_FILE.exists():
            print(f"⚠️ ملف الكوكيز غير موجود: {cls.COOKIES_FILE}")
        
        print(f"🏭 المصنع #{cls.ACCOUNT_NUMBER} | وقت البدء: {cls.START_HOUR}:00")

# ==================== 🔑 نظام تجديد التوكن ====================
class TokenManager:
    """إدارة وتجديد الـ Access Tokens"""
    
    def __init__(self):
        self.access_token = None
        self.token_expiry = None
    
    def refresh_access_token(self):
        """تجديد الـ Access Token باستخدام Refresh Token"""
        try:
            import requests
            
            if not FactoryConfig.YOUTUBE_REFRESH_TOKEN:
                print("❌ لا يوجد Refresh Token")
                return None
            
            print("🔄 جاري تجديد الـ Access Token...")
            
            url = "https://oauth2.googleapis.com/token"
            data = {
                'client_id': FactoryConfig.YOUTUBE_CLIENT_ID,
                'client_secret': FactoryConfig.YOUTUBE_CLIENT_SECRET,
                'refresh_token': FactoryConfig.YOUTUBE_REFRESH_TOKEN,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                tokens = response.json()
                self.access_token = tokens['access_token']
                self.token_expiry = datetime.now() + timedelta(seconds=3500)
                
                print("✅ تم تجديد الـ Access Token")
                return self.access_token
            else:
                print(f"❌ فشل تجديد Token: {response.status_code}")
                print(f"📝 التفاصيل: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ خطأ في تجديد Token: {e}")
            return None
    
    def get_valid_token(self):
        """الحصول على token صالح"""
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token
        return self.refresh_access_token()

# ==================== 🎬 محرك المونتاج المحسّن ====================
class VideoEditEngine:
    """محرك مونتاج متقدم للشورتس"""
    
    def __init__(self):
        self.check_ffmpeg()
    
    def check_ffmpeg(self):
        """التحقق من وجود FFmpeg"""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                          capture_output=True, text=True)
            return True
        except:
            print("⚠️ FFmpeg غير مثبت - سيتم إنشاء فيديوهات بسيطة")
            return False
    
    def download_source_video(self, keyword):
        """تحميل فيديو مصدر باستخدام الكوكيز"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'format': 'best[height<=720]',
                'outtmpl': str(FactoryConfig.TEMP_DIR / '%(id)s.%(ext)s'),
                'quiet': False,
                'no_warnings': True,
                'extract_flat': False,
                # إضافة خيارات "بشرية" لتجنب حظر GitHub Actions
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'http_headers': {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                },
                # خيارات إضافية لتجنب الحظر
                'socket_timeout': 30,
                'retries': 10,
                'fragment_retries': 10,
                'skip_unavailable_fragments': True,
                'ignoreerrors': True,
                'no_check_certificate': True,
                'prefer_ffmpeg': True,
                'geo_bypass': True,
                'geo_bypass_country': 'US',
                'throttled_rate': '1M',
                'concurrent_fragments': 1,
            }
            
            # استخدام الكوكيز إذا كان الملف موجوداً
            if FactoryConfig.COOKIES_FILE.exists():
                ydl_opts['cookiefile'] = str(FactoryConfig.COOKIES_FILE)
                print("🍪 استخدام ملف الكوكيز للتحميل")
            
            # استخدام الطريقة البديلة مع خيارات الأمان
            ydl_opts['extractor_args'] = {
                'youtube': {
                    'skip': ['dash', 'hls'],  # تجنب التنسيقات المحمية
                    'player_client': ['android', 'web'],  # استخدام عملاء متنوعين
                    'player_skip': ['configs'],
                }
            }
            
            # البحث عن فيديو
            url = f"ytsearch1:{keyword}"
            
            print(f"🔍 جاري البحث عن فيديو عن: {keyword}")
            print("🌐 استخدام إعدادات محاكاة المتصفح...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=True)
                    
                    if 'entries' in info:
                        video = info['entries'][0]
                    else:
                        video = info
                    
                    video_path = FactoryConfig.TEMP_DIR / f"{video['id']}.{video['ext']}"
                    
                    print(f"📥 تم تحميل: {video['title'][:50]}...")
                    print(f"⏱️  المدة: {video['duration']} ثانية")
                    print(f"💾 الحجم: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
                    
                    return video_path, video['duration']
                    
                except Exception as extract_error:
                    print(f"⚠️ خطأ في الاستخراج: {extract_error}")
                    
                    # محاولة بديلة باستخدام yt-dlp مباشرة كأمر فرعي
                    return self._download_with_subprocess(keyword)
                
        except Exception as e:
            print(f"❌ خطأ في التحميل: {e}")
            # محاولة بديلة
            return self._download_with_subprocess(keyword)
    
    def _download_with_subprocess(self, keyword):
        """طريقة بديلة للتحميل باستخدام yt-dlp كأمر فرعي"""
        try:
            print("🔄 المحاولة بالطريقة البديلة...")
            
            video_id = f"temp_{int(time.time())}"
            output_path = FactoryConfig.TEMP_DIR / f"{video_id}.mp4"
            url = f"ytsearch1:{keyword}"
            
            cmd = [
                'yt-dlp',
                '--quiet',
                '--no-warnings',
                '--format', 'best[height<=720][filesize<50M]',
                '--max-filesize', '50M',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '--add-header', 'Accept-Language:en-US,en;q=0.9',
                '--add-header', 'Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                '--socket-timeout', '30',
                '--retries', '10',
                '--fragment-retries', '10',
                '--skip-unavailable-fragments',
                '--ignore-errors',
                '--no-check-certificate',
                '--geo-bypass',
                '--geo-bypass-country', 'US',
                '--throttled-rate', '1M',
                '--concurrent-fragments', '1',
                '--output', str(output_path),
                url
            ]
            
            # إضافة الكوكيز إذا كان موجوداً
            if FactoryConfig.COOKIES_FILE.exists():
                cmd.insert(3, '--cookies')
                cmd.insert(4, str(FactoryConfig.COOKIES_FILE))
            
            print("🔄 جاري التحميل بالطريقة البديلة...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0 and output_path.exists():
                # الحصول على معلومات الفيديو
                info_cmd = [
                    'yt-dlp',
                    '--dump-json',
                    '--quiet',
                    '--no-warnings',
                    url
                ]
                
                info_result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=30)
                
                if info_result.returncode == 0:
                    import json
                    video_info = json.loads(info_result.stdout)
                    
                    if 'entries' in video_info:
                        video = video_info['entries'][0]
                        duration = video.get('duration', 60)
                        
                        print(f"✅ تم التحميل بالطريقة البديلة")
                        print(f"📝 العنوان: {video.get('title', 'Unknown')[:50]}...")
                        print(f"⏱️  المدة: {duration} ثانية")
                        
                        # إعادة تسمية الملف إذا لزم الأمر
                        if 'id' in video:
                            new_path = FactoryConfig.TEMP_DIR / f"{video['id']}.mp4"
                            output_path.rename(new_path)
                            return new_path, duration
                        
                        return output_path, duration
                
                # إذا لم نستطع الحصول على معلومات، نعود بقيم افتراضية
                print("✅ تم التحميل لكن دون معلومات كاملة")
                return output_path, 60
            else:
                print(f"❌ فشل التحميل البديل: {result.stderr[:200]}")
                return None, 0
                
        except Exception as e:
            print(f"❌ خطأ في التحميل البديل: {e}")
            return None, 0
    
    def create_shorts_video(self, source_path, duration):
        """تحويل الفيديو إلى شورتس بأبعاد دقيقة"""
        try:
            output_path = FactoryConfig.TEMP_DIR / f"shorts_{int(time.time())}.mp4"
            
            # حساب وقت البداية (منتصف الفيديو)
            if duration > 60:
                start_time = (duration - 60) / 2
            else:
                start_time = 0
            
            # فلتر FFmpeg لتحويل إلى 9:16 مع ضبط الذكي
            filter_complex = (
                f"scale={FactoryConfig.TARGET_RESOLUTION[0]}:{FactoryConfig.TARGET_RESOLUTION[1]}:"
                f"force_original_aspect_ratio=decrease,"
                f"pad={FactoryConfig.TARGET_RESOLUTION[0]}:{FactoryConfig.TARGET_RESOLUTION[1]}:"
                f"(ow-iw)/2:(oh-ih)/2:color=black"
            )
            
            cmd = [
                'ffmpeg',
                '-ss', str(start_time),
                '-i', str(source_path),
                '-t', '60',
                '-vf', filter_complex,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                '-y',
                str(output_path)
            ]
            
            print(f"🎬 جاري تحويل إلى شورتس (1080x1920)...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ تم إنشاء الشورتس: {output_path}")
                return output_path
            else:
                print(f"❌ خطأ في FFmpeg: {result.stderr[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ خطأ في تحويل الشورتس: {e}")
            return None
    
    def add_title_overlay(self, video_path, title):
        """إضافة عنوان على الفيديو"""
        try:
            output_path = FactoryConfig.TEMP_DIR / f"final_{video_path.name}"
            
            # هروب النص للـ FFmpeg
            safe_title = title.replace("'", "'\\''").replace(":", "\\:")
            
            filter_complex = (
                f"drawtext=text='{safe_title}':"
                f"fontcolor=white:fontsize=64:"
                f"box=1:boxcolor=black@0.7:boxborderw=10:"
                f"x=(w-text_w)/2:y=100:"
                f"enable='between(t,0,3)'"
            )
            
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vf', filter_complex,
                '-c:a', 'copy',
                '-y',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                print(f"✨ تم إضافة العنوان")
                return output_path
            else:
                return video_path
                
        except Exception as e:
            print(f"⚠️ خطأ في إضافة العنوان: {e}")
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
            print("⚠️ لا يوجد مفتاح Gemini API")
            return
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini AI جاهز")
        except ImportError:
            print("❌ google-generativeai غير مثبت")
        except Exception as e:
            print(f"⚠️ خطأ في Gemini: {e}")
    
    def generate_viral_title(self, topic):
        """توليد عنوان فيروسي"""
        if not self.model:
            return self._fallback_title(topic)
        
        try:
            prompt = f"""Create ONE viral YouTube Shorts title about: {topic}

Requirements:
1. ONE title only
2. 40-70 characters
3. Add ONE emoji at start
4. Create curiosity or controversy
5. English only

Title:"""
            
            response = self.model.generate_content(prompt)
            title = response.text.strip()
            
            # تنظيف النتيجة
            title = title.replace('"', '').replace("'", "").strip()
            
            # إضافة إيموجي إذا لم يكن موجود
            if not any(emoji in title for emoji in ["😱", "🚀", "⚠️", "💥"]):
                title = "😱 " + title
            
            print(f"🧠 AI Generated: {title}")
            return title[:80]
            
        except Exception as e:
            print(f"❌ خطأ في توليد العنوان: {e}")
            return self._fallback_title(topic)
    
    def _fallback_title(self, topic):
        """عناوين احتياطية"""
        templates = [
            f"😱 This {topic} Secret Will Make You Rich",
            f"🚀 How to Make Money With {topic}",
            f"⚠️ The Truth About {topic}",
            f"💥 {topic} Strategy That Works"
        ]
        return random.choice(templates)
    
    def generate_description(self, title, topic):
        """توليد وصف الفيديو"""
        hashtags = [
            f"#{topic.replace(' ', '')}",
            "#shorts", "#viral", "#money",
            "#success", "#business", "#tech"
        ]
        
        random.shuffle(hashtags)
        selected_hashtags = hashtags[:8]
        
        description = f"""{title}

🔔 Subscribe for more!

{' '.join(selected_hashtags)}
"""
        
        return description.strip()

# ==================== 📤 نظام الرفع الحقيقي الكامل ====================
class YouTubeUploader:
    """نظام الرفع الكامل باستخدام YouTube API"""
    
    def __init__(self):
        self.token_manager = TokenManager()
        print("✅ YouTube Uploader مهيأ")
    
    def upload_video(self, video_path, title, description, tags):
        """رفع فيديو حقيقي لليوتيوب"""
        try:
            # الحصول على token صالح
            access_token = self.token_manager.get_valid_token()
            if not access_token:
                print("❌ لا يمكن الحصول على Access Token")
                return None
            
            print(f"🚀 بدء الرفع الحقيقي: {title[:50]}...")
            
            # استخدام YouTube API للرفع
            return self._upload_with_youtube_api(video_path, title, description, tags, access_token)
                
        except Exception as e:
            print(f"❌ خطأ في الرفع: {e}")
            return None
    
    def _upload_with_youtube_api(self, video_path, title, description, tags, access_token):
        """الرفع باستخدام YouTube Data API v3"""
        try:
            import requests
            
            # معلومات الفيديو
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
                    "embeddable": True
                }
            }
            
            # رفع الفيديو
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            # 1. طلب رفع الفيديو
            upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"
            params = {
                "part": "snippet,status",
                "uploadType": "resumable"
            }
            
            # إنشاء جلسة رفع
            session_response = requests.post(
                upload_url,
                headers=headers,
                params=params,
                data=json.dumps(video_metadata)
            )
            
            if session_response.status_code != 200:
                print(f"❌ فشل إنشاء جلسة الرفع: {session_response.status_code}")
                return None
            
            upload_url = session_response.headers.get("Location")
            if not upload_url:
                print("❌ لا يوجد رابط رفع")
                return None
            
            # 2. رفع ملف الفيديو
            print("📤 جاري رفع ملف الفيديو...")
            with open(video_path, 'rb') as video_file:
                video_data = video_file.read()
            
            upload_response = requests.put(
                upload_url,
                headers={"Content-Type": "video/*"},
                data=video_data
            )
            
            if upload_response.status_code == 200:
                video_info = upload_response.json()
                video_id = video_info["id"]
                
                print(f"✅ تم الرفع بنجاح!")
                print(f"🎬 ID: {video_id}")
                print(f"🔗 https://youtu.be/{video_id}")
                
                return {
                    'id': video_id,
                    'title': title,
                    'url': f'https://youtu.be/{video_id}',
                    'real': True
                }
            else:
                print(f"❌ فشل الرفع: {upload_response.status_code}")
                return None
                
        except ImportError:
            print("❌ مكتبة requests غير مثبتة")
            return None
        except Exception as e:
            print(f"❌ خطأ في YouTube API: {e}")
            return None

# ==================== 💾 نظام حفظ الحالة ====================
class StateManager:
    """إدارة حالة النظام ومنع التكرار"""
    
    def __init__(self):
        self.state_file = FactoryConfig.LOGS_DIR / "uploaded_videos.json"
        self.uploaded_videos = self.load_state()
    
    def load_state(self):
        """تحميل الحالة السابقة"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_state(self):
        """حفظ الحالة الحالية"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.uploaded_videos[-100:], f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ خطأ في حفظ الحالة: {e}")
            return False
    
    def is_video_uploaded(self, video_id):
        """التحقق إذا كان الفيديو مرفوعاً مسبقاً"""
        return any(video.get('id') == video_id for video in self.uploaded_videos)
    
    def add_uploaded_video(self, video_data):
        """إضافة فيديو جديد إلى السجل"""
        self.uploaded_videos.append({
            'id': video_data.get('id'),
            'title': video_data.get('title'),
            'timestamp': datetime.now().isoformat(),
            'account': FactoryConfig.ACCOUNT_NUMBER
        })
        self.save_state()
    
    def get_today_uploads(self):
        """الحصول على عدد الرفعات اليوم"""
        today = datetime.now().date()
        today_uploads = [
            video for video in self.uploaded_videos
            if datetime.fromisoformat(video['timestamp']).date() == today
        ]
        return len(today_uploads)

# ==================== ⏰ نظام التوزيع الذكي ====================
class DistributedScheduler:
    """نظام جدولة مع توزيع الحسابات"""
    
    def __init__(self):
        self.account_number = FactoryConfig.ACCOUNT_NUMBER
        self.start_hour = FactoryConfig.START_HOUR
        
        # الانتظار حتى وقت البدء
        self.wait_until_start_time()
    
    def wait_until_start_time(self):
        """الانتظار حتى وقت البدء المحدد"""
        now = datetime.now()
        target_time = now.replace(hour=self.start_hour, minute=0, second=0, microsecond=0)
        
        if target_time < now:
            target_time += timedelta(days=1)
        
        wait_seconds = (target_time - now).total_seconds()
        
        if wait_seconds > 0:
            wait_hours = wait_seconds // 3600
            wait_minutes = (wait_seconds % 3600) // 60
            
            print(f"⏰ الحساب #{self.account_number} ينتظر حتى {self.start_hour}:00")
            print(f"   ({wait_hours:.0f} ساعة {wait_minutes:.0f} دقيقة)")
            
            time.sleep(wait_seconds)
        
        print(f"🚀 الحساب #{self.account_number} بدأ العمل في {self.start_hour}:00")
    
    def get_next_upload_time(self):
        """حساب وقت الرفع التالي"""
        variation = random.randint(-FactoryConfig.VARIATION, FactoryConfig.VARIATION)
        interval = FactoryConfig.BASE_INTERVAL + variation
        
        minutes = int(interval // 60)
        print(f"⏰ التالي بعد: {minutes} دقيقة")
        
        return interval

# ==================== 🏭 المصنع الرئيسي ====================
class MoneyFactory:
    """المصنع الرئيسي الكامل"""
    
    def __init__(self):
        FactoryConfig.setup_directories()
        
        # أنظمة المصنع
        self.video_engine = VideoEditEngine()
        self.ai_factory = AIContentFactory()
        self.youtube_uploader = YouTubeUploader()
        self.state_manager = StateManager()
        self.scheduler = DistributedScheduler()
        
        # إحصائيات
        self.stats = {
            'total_produced': 0,
            'real_uploads': 0,
            'daily_target': FactoryConfig.DAILY_TARGET,
            'start_time': datetime.now()
        }
        
        self.show_factory_banner()
    
    def show_factory_banner(self):
        """عرض بانر المصنع"""
        banner = f"""
        {'='*70}
        🏭   YouTube Shorts Factory #{FactoryConfig.ACCOUNT_NUMBER}   🏭
        {'='*70}
        
        ⚙️  الإعدادات:
        • الحساب: #{FactoryConfig.ACCOUNT_NUMBER}
        • وقت البدء: {FactoryConfig.START_HOUR}:00
        • الهدف اليومي: {FactoryConfig.DAILY_TARGET} شورتس
        • التوكن: {'✅' if FactoryConfig.YOUTUBE_REFRESH_TOKEN else '❌'}
        • AI: {'✅' if FactoryConfig.GEMINI_API_KEY else '❌'}
        
        📊 اليوم: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        {'='*70}
        """
        print(banner)
    
    def produce_shorts(self, index):
        """إنتاج شورت واحد"""
        try:
            print(f"\n🎬 جولة الإنتاج #{index}")
            print("-"*50)
            
            # 1. اختيار موضوع
            topic = random.choice(FactoryConfig.ENGLISH_TOPICS)
            print(f"📌 الموضوع: {topic}")
            
            # 2. توليد محتوى
            title = self.ai_factory.generate_viral_title(topic)
            description = self.ai_factory.generate_description(title, topic)
            
            tags = [
                topic.lower().replace(" ", ""),
                "shorts", "viral", "money",
                "success", "business"
            ]
            
            print(f"📝 العنوان: {title}")
            
            # 3. تحميل ومعالجة الفيديو
            print("📥 جاري تحميل فيديو مصدر...")
            source_path, duration = self.video_engine.download_source_video(topic)
            
            if not source_path:
                print("❌ فشل تحميل الفيديو")
                return False
            
            print("🎬 جاري تحويل إلى شورتس...")
            shorts_path = self.video_engine.create_shorts_video(source_path, duration)
            
            if not shorts_path:
                print("❌ فشل تحويل الشورتس")
                return False
            
            print("✨ جاري إضافة العنوان...")
            final_video = self.video_engine.add_title_overlay(shorts_path, title)
            
            # 4. الرفع لليوتيوب
            print("🚀 بدء الرفع...")
            result = self.youtube_uploader.upload_video(final_video, title, description, tags)
            
            # 5. تنظيف
            self.cleanup_files([source_path, shorts_path, final_video])
            
            if result:
                self.stats['total_produced'] += 1
                
                if result.get('real'):
                    self.stats['real_uploads'] += 1
                    self.state_manager.add_uploaded_video(result)
                
                print(f"✅ اكتملت الجولة #{index}")
                print(f"📊 الإجمالي: {self.stats['total_produced']} شورتس")
                
                return True
            else:
                print("❌ فشلت الجولة")
                return False
                
        except Exception as e:
            print(f"💥 خطأ في الإنتاج: {e}")
            return False
    
    def cleanup_files(self, files):
        """تنظيف الملفات المؤقتة"""
        for file_path in files:
            if file_path and file_path.exists():
                try:
                    file_path.unlink()
                except:
                    pass
    
    def run_production_cycle(self):
        """دورة الإنتاج الكاملة"""
        print("\n🏭 بدء دورة الإنتاج...")
        
        produced_count = 0
        errors_count = 0
        
        try:
            while produced_count < self.stats['daily_target']:
                # التحقق من الرفعات اليومية
                today_uploads = self.state_manager.get_today_uploads()
                if today_uploads >= self.stats['daily_target']:
                    print(f"🎯 تم تحقيق الهدف اليومي: {today_uploads} شورتس")
                    break
                
                # إنتاج شورت
                success = self.produce_shorts(produced_count + 1)
                
                if success:
                    produced_count += 1
                else:
                    errors_count += 1
                
                # إعادة المحاولة بعد أخطاء
                if errors_count >= 2:
                    print("🚨 كثرة الأخطاء، توقف مؤقت 5 دقائق")
                    time.sleep(300)
                    errors_count = 0
                
                # انتظار الجولة التالية
                if produced_count < self.stats['daily_target']:
                    wait_time = self.scheduler.get_next_upload_time()
                    print(f"\n😴 انتظار الجولة التالية...")
                    
                    # انتظار مع عداد
                    for remaining in range(int(wait_time), 0, -60):
                        if remaining % 300 == 0 or remaining <= 60:
                            mins = remaining // 60
                            if mins > 0:
                                print(f"   ⏳ باقي {mins} دقيقة...")
                            else:
                                print(f"   ⏳ {remaining} ثانية...")
                        time.sleep(min(60, remaining))
                    
                    print("\n" + "="*50)
            
        except KeyboardInterrupt:
            print("\n\n🛑 تم إيقاف الإنتاج")
        
        self.show_production_report(produced_count)
    
    def show_production_report(self, produced_count):
        """عرض تقرير الإنتاج"""
        elapsed = datetime.now() - self.stats['start_time']
        hours = elapsed.total_seconds() / 3600
        
        print("\n" + "="*70)
        print("📊 تقرير الإنتاج النهائي")
        print("="*70)
        
        print(f"🏭 المصنع: #{FactoryConfig.ACCOUNT_NUMBER}")
        print(f"⏱️  وقت التشغيل: {hours:.1f} ساعة")
        print(f"🎬 الشورتات المنتجة: {produced_count}")
        print(f"📤 الرفع الحقيقي: {self.stats['real_uploads']}")
        
        if self.stats['real_uploads'] > 0:
            earnings = self.stats['real_uploads'] * 0.75
            monthly = earnings * 30
            
            print(f"\n💰 الأرباح المتوقعة:")
            print(f"   • اليوم: ${earnings:.2f}")
            print(f"   • الشهر: ${monthly:.2f}")
        
        print(f"\n📁 السجلات: {FactoryConfig.LOGS_DIR}")
        print("="*70)

# ==================== 🚀 نقطة التشغيل ====================
def setup_environment():
    """إعداد بيئة التشغيل"""
    print("\n🔧 إعداد بيئة المصنع...")
    
    # تثبيت المكتبات المطلوبة
    libraries = ["yt-dlp", "google-generativeai", "requests"]
    
    for lib in libraries:
        try:
            __import__(lib.replace("-", "_"))
            print(f"✅ {lib} مثبت")
        except ImportError:
            print(f"📦 تثبيت {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
    
    # التحقق من المفاتيح
    if not FactoryConfig.YOUTUBE_REFRESH_TOKEN:
        print("❌ لا يوجد Refresh Token - الرفع الحقيقي لن يعمل")
    
    if not FactoryConfig.GEMINI_API_KEY:
        print("⚠️ لا يوجد مفتاح Gemini - العناوين ستكون افتراضية")
    
    print("✅ اكتمل الإعداد")

def main():
    """الدالة الرئيسية"""
    print("\n" + "="*70)
    print("🏭 YouTube Shorts Money Factory v5.0")
    print("="*70)
    
    # التحقق من المتغيرات
    if not FactoryConfig.YOUTUBE_CLIENT_ID:
        print("❌ YOUTUBE_CLIENT_ID غير موجود")
        return
    
    # الإعداد التلقائي
    setup_environment()
    
    # إنشاء وتشغيل المصنع
    factory = MoneyFactory()
    factory.run_production_cycle()
    
    print("\n🏭 انتهت الدورة اليومية")

# ==================== التشغيل التلقائي ====================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 خطأ جسيم: {e}")
        sys.exit(1)
