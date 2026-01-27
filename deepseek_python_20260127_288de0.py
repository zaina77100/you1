#!/usr/bin/env python3
"""
🏭 YouTube AI Short Creator v9.0 - GRIT & GOLD FACTORY
"""

import os
import sys
import json
import time
import random
import logging
import pickle
import subprocess
import tempfile
import shutil
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

print("🔍 جارٍ استيراد المكتبات...")

# ==================== استيراد المكتبات ====================
try:
    import google.genai as genai
    print("✅ google.genai - OK")
except ImportError as e:
    print(f"❌ خطأ: {e}")
    print("📦 قم بتثبيت: pip install google-genai")
    sys.exit(1)

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    print("✅ googleapiclient - OK")
except ImportError as e:
    print(f"❌ خطأ: {e}")
    print("📦 قم بتثبيت: pip install google-api-python-client google-auth-oauthlib")
    sys.exit(1)

try:
    import yt_dlp
    print("✅ yt-dlp - OK")
except ImportError as e:
    print(f"❌ خطأ: {e}")
    sys.exit(1)

try:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
    print("✅ moviepy - OK")
except ImportError as e:
    print(f"❌ خطأ: {e}")
    sys.exit(1)

# المكتبات الاختيارية
try:
    import cv2
    CV2_AVAILABLE = True
    print("✅ opencv-python - OK")
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ opencv-python غير متوفر")

try:
    from PIL import Image
    PIL_AVAILABLE = True
    print("✅ Pillow - OK")
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ Pillow غير متوفر")

try:
    import whisper
    WHISPER_AVAILABLE = True
    print("✅ Whisper - OK")
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️ Whisper غير متوفر")

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    print("✅ Mediapipe - OK")
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("⚠️ Mediapipe غير متوفر")

# ==================== إعدادات GRIT & GOLD ====================
class GritGoldConfig:
    """إعدادات إمبراطورية Grit & Gold"""
    
    # إعدادات القناة
    CHANNEL_NAME = "Grit & Gold"
    CHANNEL_ID = ""  # سيتم تعبئته تلقائياً
    TARGET_LANGUAGE = "en"
    NICHE = "Business | Money | Mindset | Success"
    BRAND_HASHTAG = "#GritAndGold"
    
    # قنوات المصدر (بودكاست البزنس العالمية)
    SOURCE_CHANNELS = [
        "https://www.youtube.com/@AlexHormozi",
        "https://www.youtube.com/@DiaryOfACEO",
        "https://www.youtube.com/@Valuetainment",
        "https://www.youtube.com/@TomBilyeu",
        "https://www.youtube.com/@GaryVee",
        "https://www.youtube.com/@ImpactTheory",
        "https://www.youtube.com/@ImanGadzhi",
        "https://www.youtube.com/@GrantCardone"
    ]
    
    # كلمات مفتاحية للبحث
    SEARCH_KEYWORDS = [
        "how to make money", "business secrets", "entrepreneur mindset",
        "financial freedom", "get rich", "millionaire habits",
        "success motivation", "startup advice", "investing tips"
    ]
    
    # إعدادات الفيديو
    SHORT_DURATION = 59  # أقل من 60 ثانية لتصنيف Shorts
    TARGET_RESOLUTION = (1080, 1920)  # 9:16 عمودي
    MIN_VIEWS_THRESHOLD = 10000  # خفضنا الحد الأدنى للمشاهدات
    MAX_VIDEOS_PER_DAY = 12  # فيديو كل ساعتين
    
    # إعدادات الذكاء الاصطناعي
    GEMINI_MODEL = "gemini-pro"
    CONTROVERSY_LEVEL = 0.8  # مستوى الجدال (0-1)
    
    # المسارات
    BASE_DIR = Path.cwd()
    CONFIG_DIR = BASE_DIR / "config_grit_gold"
    OUTPUT_DIR = BASE_DIR / "output_grit_gold"
    TEMP_DIR = BASE_DIR / "temp_grit_gold"
    LOGS_DIR = BASE_DIR / "logs_grit_gold"
    DB_DIR = BASE_DIR / "database_grit_gold"
    
    # ملفات المصادقة
    CREDENTIALS_FILE = CONFIG_DIR / "youtube_credentials.json"
    TOKEN_FILE = CONFIG_DIR / "token.pickle"
    GEMINI_KEY_FILE = CONFIG_DIR / "gemini_key.txt"
    
    # إعدادات الرفع
    AUTO_UPLOAD = True
    AUTO_DELETE_AFTER_UPLOAD = True
    UPLOAD_SCHEDULE = "2h"  # كل ساعتين
    RANDOM_DELAY_RANGE = (-600, 600)  # ±10 دقائق عشوائية
    
    def __init__(self):
        self.create_directories()
        self.load_environment()
    
    def create_directories(self):
        """إنشاء المجلدات الهيكلية"""
        for directory in [self.CONFIG_DIR, self.OUTPUT_DIR, self.TEMP_DIR, 
                         self.LOGS_DIR, self.DB_DIR]:
            directory.mkdir(exist_ok=True, parents=True)
    
    def load_environment(self):
        """تحميل مفاتيح API من البيئة"""
        # Gemini API - من المتغيرات البيئية مباشرة
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        
        # إنشاء ملف Gemini key إذا كان موجوداً في المتغيرات
        if self.GEMINI_API_KEY and not self.GEMINI_KEY_FILE.exists():
            with open(self.GEMINI_KEY_FILE, 'w') as f:
                f.write(self.GEMINI_API_KEY)
        
        # إنشاء ملف youtube_credentials من الـ secrets إذا كان موجوداً
        if not self.CREDENTIALS_FILE.exists():
            youtube_creds = os.getenv('YOUTUBE_CREDENTIALS')
            if youtube_creds:
                try:
                    with open(self.CREDENTIALS_FILE, 'w') as f:
                        f.write(youtube_creds)
                    print(f"✅ تم إنشاء {self.CREDENTIALS_FILE} من الـ secrets")
                except Exception as e:
                    print(f"⚠️ خطأ في إنشاء ملف اليوتيوب: {e}")
            else:
                print(f"⚠️ ملف {self.CREDENTIALS_FILE} غير موجود")
                print("📋 تأكد من إضافة YOUTUBE_CREDENTIALS إلى GitHub Secrets")

# ==================== نظام التسجيل ====================
class GritGoldLogger:
    """نظام تسجيل احترافي"""
    
    def __init__(self, config):
        self.config = config
        self.setup_logging()
    
    def setup_logging(self):
        """إعداد نظام التسجيل"""
        log_file = self.config.LOGS_DIR / f"grit_gold_{datetime.now().strftime('%Y%m')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('GritGoldFactory')
    
    def log_video_creation(self, video_data: Dict):
        """تسجيل إنشاء فيديو"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'video_id': video_data.get('id', ''),
            'source': video_data.get('source', ''),
            'title': video_data.get('title', '')[:100],
            'views': video_data.get('views', 0),
            'duration': video_data.get('duration', 0),
            'upload_status': video_data.get('upload_status', 'pending')
        }
        
        db_file = self.config.DB_DIR / "videos_created.json"
        videos = []
        
        if db_file.exists():
            with open(db_file, 'r', encoding='utf-8') as f:
                videos = json.load(f)
        
        videos.append(log_entry)
        
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(videos[-1000:], f, indent=2, ensure_ascii=False)

# ==================== محرك الذكاء الاصطناعي ====================
class AIContentEngine:
    """محرك الذكاء الاصطناعي لصناعة محتوى فيروسي"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('AIContentEngine')
        self.gemini_client = None
        self.whisper_model = None
        
        self.init_gemini()
        self.init_whisper()
    
    def init_gemini(self):
        """تهيئة Gemini"""
        if not self.config.GEMINI_API_KEY:
            self.logger.warning("⚠️ مفتاح Gemini غير متوفر")
            return
        
        try:
            # ✅ التصحيح هنا: استخدام genai.configure مباشرة
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            self.gemini_client = genai.GenerativeModel(self.config.GEMINI_MODEL)
            self.logger.info("✅ Gemini مهيأ")
        except Exception as e:
            self.logger.error(f"❌ خطأ في تهيئة Gemini: {e}")
    
    def init_whisper(self):
        """تهيئة Whisper للترجمة"""
        if not WHISPER_AVAILABLE:
            self.logger.warning("⚠️ Whisper غير متوفر، سيتم تعطيل الترجمة الصوتية")
            return
        
        try:
            self.whisper_model = whisper.load_model("base")
            self.logger.info("✅ Whisper مهيأ للترجمة")
        except Exception as e:
            self.logger.warning(f"⚠️ خطأ في Whisper: {e}")
    
    def generate_viral_metadata(self, video_context: str) -> Dict:
        """توليد بيانات فيروسية للفيديو"""
        if not self.gemini_client:
            self.logger.info("🧠 استخدام البيانات الافتراضية (Gemini غير متوفر)")
            return self._get_default_metadata()
        
        try:
            prompt = self._create_viral_prompt(video_context)
            response = self.gemini_client.generate_content(prompt)
            
            metadata = self._parse_ai_response(response.text)
            metadata['title'] = self._optimize_title_for_ctr(metadata['title'])
            
            self.logger.info(f"🧠 العنوان المولد: {metadata['title'][:60]}...")
            return metadata
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في توليد المحتوى: {e}")
            return self._get_default_metadata()
    
    def _create_viral_prompt(self, context: str) -> str:
        """إنشاء prompt فيروسي"""
        return f"""
        أنشئ بيانات فيروسية لفيديو YouTube Short عن:
        {context[:200]}
        
        المخرجات بصيغة JSON:
        {{
            "title": "عنوان جذاب بالانجليزية",
            "description": "وصف قصير",
            "tags": ["tag1", "tag2", "tag3"],
            "captions": ["caption1", "caption2", "caption3"]
        }}
        """
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """تحليل استجابة الذكاء الاصطناعي"""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return self._get_default_metadata()
    
    def _optimize_title_for_ctr(self, title: str) -> str:
        """تحسين العنوان لمعدل النقر"""
        emojis = ["🚀", "💰", "🔥", "🎯", "⚡"]
        emoji = random.choice(emojis)
        
        if len(title) > 50:
            title = title[:47] + "..."
        
        if not any(char.isdigit() for char in title):
            numbers = ["1", "3", "5", "7"]
            if random.random() > 0.5:
                title = title.replace("This", f"This {random.choice(numbers)}")
        
        return f"{emoji} {title}"
    
    def _get_default_metadata(self) -> Dict:
        """بيانات افتراضية"""
        titles = [
            "The Truth About Making Money Online",
            "Business Secrets They Don't Want You To Know",
            "How I Went From $0 to $10k/Month",
            "The 1% Rule for Financial Freedom",
            "Stop Wasting Time - Start Making Money"
        ]
        
        return {
            'title': random.choice(titles),
            'description': f"Success requires GRIT. Join Grit & Gold for daily business wisdom. #GritAndGold",
            'tags': ['Business', 'Success', 'Money', 'Entrepreneur', 'Motivation', 'GritAndGold'],
            'captions': ['You need to take action', 'Stop making excuses', 'The money is waiting for you']
        }

# ==================== نظام سحب المحتوى ====================
class ContentHunter:
    """صياد المحتوى من YouTube"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('ContentHunter')
        self.avoid_history = []
        self.load_avoid_history()
    
    def load_avoid_history(self):
        """تحميل تاريخ الفيديوهات المسحوبة"""
        history_file = self.config.DB_DIR / "downloaded_history.txt"
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                self.avoid_history = [line.strip() for line in f.readlines()]
    
    def save_to_history(self, video_id: str):
        """حفظ الفيديو في التاريخ"""
        history_file = self.config.DB_DIR / "downloaded_history.txt"
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(f"{video_id}\n")
        self.avoid_history.append(video_id)
    
    def find_viral_content(self) -> Optional[Dict]:
        """البحث عن محتوى فيروسي"""
        try:
            # استخدام قناة ثابتة للاختبار
            channel_url = "https://www.youtube.com/@AlexHormozi"
            
            self.logger.info(f"🔍 البحث في {channel_url}")
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'force_generic_extractor': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"{channel_url}/videos", download=False)
                
                if not info or 'entries' not in info:
                    return None
                
                videos = []
                for entry in info['entries'][:20]:
                    if self._is_good_video(entry):
                        videos.append(entry)
                
                if not videos:
                    return None
                
                best_video = random.choice(videos)  # اختيار عشوائي للاختبار
                self.logger.info(f"🎯 تم اختيار فيديو: {best_video['title'][:60]}...")
                return best_video
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في البحث: {e}")
            return None
    
    def _is_good_video(self, video_info: Dict) -> bool:
        """فحص إذا كان الفيديو جيداً"""
        required = ['id', 'title', 'duration', 'view_count']
        if not all(field in video_info for field in required):
            return False
        
        duration = video_info['duration']
        if duration < 60 or duration > 1200:
            return False
        
        views = video_info['view_count']
        if views < self.config.MIN_VIEWS_THRESHOLD:
            return False
        
        return True
    
    def download_video_segment(self, video_url: str, start_time: int = 0) -> Optional[str]:
        """تحميل مقطع من الفيديو"""
        try:
            temp_dir = tempfile.mkdtemp(dir=str(self.config.TEMP_DIR))
            output_path = Path(temp_dir) / "video.mp4"
            
            ydl_opts = {
                'format': 'best[height<=720]',
                'outtmpl': str(output_path.with_suffix('.%(ext)s')),
                'quiet': True,
                'no_warnings': True,
                'external_downloader': 'ffmpeg',
                'external_downloader_args': [
                    '-ss', str(start_time),
                    '-t', str(self.config.SHORT_DURATION),
                ]
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            if output_path.exists():
                self.logger.info(f"✅ تم تحميل المقطع")
                return str(output_path)
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في التحميل: {e}")
            return None

# ==================== محرك معالجة الفيديو ====================
class VideoProcessor:
    """محرك معالجة وتحويل الفيديوهات"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('VideoProcessor')
    
    def process_video_for_shorts(self, input_path: str, metadata: Dict) -> Optional[str]:
        """معالجة الفيديو وتحويله لـ Shorts"""
        try:
            self.logger.info("🎬 بدء معالجة الفيديو...")
            
            output_filename = f"grit_gold_{int(time.time())}.mp4"
            output_path = self.config.OUTPUT_DIR / output_filename
            
            # قص الفيديو
            cropped_path = self._basic_crop(input_path)
            
            # إضافة علامة مائية
            final_path = self._add_watermark(cropped_path)
            
            # نقل للخارج
            shutil.move(final_path, output_path)
            
            # تنظيف
            self._cleanup_temp_files([input_path, cropped_path])
            
            self.logger.info(f"✅ الفيديو جاهز: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في المعالجة: {e}")
            return None
    
    def _basic_crop(self, video_path: str) -> str:
        """قص أساسي"""
        temp_output = Path(tempfile.mktemp(suffix='.mp4', dir=str(self.config.TEMP_DIR)))
        
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vf', 'crop=ih*9/16:ih,scale=1080:1920',
            '-c:a', 'copy',
            str(temp_output)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True, timeout=60)
        return str(temp_output)
    
    def _add_watermark(self, video_path: str) -> str:
        """إضافة علامة مائية"""
        temp_output = Path(tempfile.mktemp(suffix='.mp4', dir=str(self.config.TEMP_DIR)))
        
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vf', f"drawtext=text='Grit & Gold':fontcolor=white@0.7:fontsize=30:x=20:y=20",
            '-c:a', 'copy',
            str(temp_output)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True, timeout=60)
        return str(temp_output)
    
    def _cleanup_temp_files(self, file_paths: List[str]):
        """تنظيف الملفات المؤقتة"""
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass

# ==================== نظام الرفع لـ YouTube ====================
class YouTubeUploader:
    """نظام الرفع التلقائي لـ YouTube"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('YouTubeUploader')
        self.youtube_service = None
        
        if self.config.AUTO_UPLOAD and self.config.CREDENTIALS_FILE.exists():
            self.init_youtube_service()
        else:
            self.logger.warning("⚠️ الرفع التلقائي معطل (مفاتيح غير متوفرة)")
    
    def init_youtube_service(self):
        """تهيئة خدمة YouTube API"""
        try:
            creds = None
            
            if self.config.TOKEN_FILE.exists():
                with open(self.config.TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.config.CREDENTIALS_FILE),
                        ['https://www.googleapis.com/auth/youtube.upload']
                    )
                    creds = flow.run_local_server(port=0)
                
                with open(self.config.TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.youtube_service = build('youtube', 'v3', credentials=creds)
            self.logger.info("✅ خدمة YouTube API مهيأة")
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تهيئة YouTube API: {e}")
    
    def upload_video(self, video_path: str, metadata: Dict) -> Optional[str]:
        """رفع الفيديو لـ YouTube"""
        if not self.youtube_service:
            self.logger.warning("⏸️ تخطي الرفع (الخدمة غير مهيأة)")
            return "simulated_video_id"
        
        try:
            self.logger.info(f"📤 جاري رفع الفيديو: {os.path.basename(video_path)}")
            
            body = {
                'snippet': {
                    'title': metadata.get('title', 'Grit & Gold Motivation'),
                    'description': metadata.get('description', ''),
                    'tags': metadata.get('tags', []),
                    'categoryId': '27',
                    'defaultLanguage': 'en'
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False,
                }
            }
            
            media = MediaFileUpload(video_path, mimetype='video/mp4')
            
            request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = request.execute()
            video_id = response['id']
            video_url = f"https://youtube.com/shorts/{video_id}"
            
            self.logger.info(f"✅ تم الرفع بنجاح: {video_url}")
            
            if self.config.AUTO_DELETE_AFTER_UPLOAD:
                try:
                    os.remove(video_path)
                    self.logger.info("🗑️ تم حذف الفيديو المحلي")
                except:
                    pass
            
            return video_id
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في الرفع: {e}")
            return None

# ==================== المحرك الرئيسي ====================
class GritGoldFactory:
    """المصنع الرئيسي"""
    
    def __init__(self):
        self.config = GritGoldConfig()
        self.logger = GritGoldLogger(self.config).logger
        self.ai_engine = AIContentEngine(self.config)
        self.content_hunter = ContentHunter(self.config)
        self.video_processor = VideoProcessor(self.config)
        self.uploader = YouTubeUploader(self.config)
        
        self.total_videos_created = 0
        self.start_time = datetime.now()
    
    def run_production_cycle(self) -> bool:
        """تشغيل دورة إنتاج كاملة"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("🏭 بدء دورة إنتاج Grit & Gold")
            self.logger.info("=" * 60)
            
            # 1. البحث عن محتوى
            self.logger.info("🔎 المرحلة 1: البحث عن محتوى فيروسي...")
            video_info = self.content_hunter.find_viral_content()
            
            if not video_info:
                self.logger.warning("⚠️ لم يتم العثور على محتوى مناسب")
                # استخدام فيديو تجريبي
                video_info = {
                    'id': 'test_video_001',
                    'title': 'How to Build a Business From Scratch',
                    'duration': 300,
                    'view_count': 100000
                }
                self.logger.info("📝 استخدام فيديو تجريبي للاختبار")
            
            # 2. توليد بيانات
            self.logger.info("🧠 المرحلة 2: توليد محتوى ذكي...")
            metadata = self.ai_engine.generate_viral_metadata(video_info['title'])
            
            # 3. تحميل المقطع (محاكاة للاختبار)
            self.logger.info("📥 المرحلة 3: محاكاة التحميل...")
            
            # إذا كان اختباراً، تخطي التحميل الفعلي
            if 'test' in video_info['id']:
                video_path = None
                self.logger.info("🔄 تخطي التحميل (وضع الاختبار)")
            else:
                video_url = f"https://youtube.com/watch?v={video_info['id']}"
                start_time = random.randint(0, 100)
                video_path = self.content_hunter.download_video_segment(video_url, start_time)
            
            # 4. معالجة الفيديو (إذا تم التحميل)
            if video_path:
                self.logger.info("🎬 المرحلة 4: معالجة الفيديو...")
                processed_path = self.video_processor.process_video_for_shorts(video_path, metadata)
                
                if processed_path:
                    # 5. رفع الفيديو
                    self.logger.info("🚀 المرحلة 5: رفع الفيديو...")
                    video_id = self.uploader.upload_video(processed_path, metadata)
                    
                    if video_id:
                        self.total_videos_created += 1
                        self.logger.info(f"🎉 تم إنشاء ورفع الفيديو #{self.total_videos_created}")
                        return True
            else:
                self.logger.info("✅ انتهت دورة المحاكاة بنجاح")
                self.total_videos_created += 1
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"💥 خطأ في دورة الإنتاج: {e}")
            return False

# ==================== نقطة الدخول الرئيسية ====================
if __name__ == "__main__":
    # عرض البانر
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                    🏭 GRIT & GOLD FACTORY                  ║
    ║         YouTube AI Short Creator v9.0 - Global Edition     ║
    ║                                                            ║
    ║  🔥 Business | Money | Mindset | Success                   ║
    ║  🎯 Target: Western Audience (18-35)                       ║
    ║  🚀 Production: 12 videos/day                              ║
    ║  💰 Goal: $1,000 - $3,000/month                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print("🔍 التحقق من المتطلبات...")
    
    # إنشاء المصنع
    factory = GritGoldFactory()
    
    # إذا كان هناك مدخل من GitHub Actions، استخدمه
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        choice = "1"
    else:
        # سؤال عن وضع التشغيل
        print("\n" + "="*60)
        print("🎛️  خيارات التشغيل:")
        print("1. دورة واحدة (اختبار)")
        print("2. الإنتاج المستمر (تلقائي)")
        print("3. الخروج")
        
        try:
            choice = input("\nاختر الخيار [1-3]: ").strip()
        except EOFError:
            # إذا كان GitHub Actions، استخدم الافتراضي
            choice = "1"
            print(f"\n🔧 استخدام الخيار الافتراضي: {choice}")
    
    if choice == "1":
        print("🔄 تشغيل دورة اختبار واحدة...")
        success = factory.run_production_cycle()
        if success:
            print("✅ الدورة اكتملت بنجاح!")
        else:
            print("⚠️ الدورة انتهت بتحذيرات")
            
    elif choice == "2":
        print("🏭 بدء المصنع - الإنتاج التلقائي المستمر")
        print("⚠️  اضغط Ctrl+C لإيقاف المصنع")
        print("="*60)
        
        factory.run_continuous_production()
        
    else:
        print("👋 مع السلامة!")
        sys.exit(0)
