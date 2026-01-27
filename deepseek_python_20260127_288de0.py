#!/usr/bin/env python3
"""
🏭 YouTube AI Short Creator v9.0 - GRIT & GOLD FACTORY
مطبعة فيديوهات شورت فيروسية للأجانب في مجال البزنس والشباب
يعمل تلقائياً على قناة واحدة - إصدار المؤسسة النهائي
"""

import os
import sys
import json
import time
import random
import logging
import pickle
import subprocess
import hashlib
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import concurrent.futures

# ==================== استيراد المكتبات ====================
try:
    import google.generativeai as genai
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import yt_dlp
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import whisper
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
    import mediapipe as mp
except ImportError as e:
    print(f"❌ مكتبة مفقودة: {e}")
    print("📦 قم بتثبيت: pip install google-generativeai google-api-python-client yt-dlp opencv-python pillow openai-whisper moviepy mediapipe")
    sys.exit(1)

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
    MIN_VIEWS_THRESHOLD = 50000  # أقل فيديو مشاهدات نقبله
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
        # Gemini API
        if self.GEMINI_KEY_FILE.exists():
            with open(self.GEMINI_KEY_FILE, 'r') as f:
                os.environ['GEMINI_API_KEY'] = f.read().strip()
        
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        
        # YouTube API
        if not self.CREDENTIALS_FILE.exists():
            print(f"⚠️ ملف {self.CREDENTIALS_FILE} غير موجود")
            print("📋 حمل ملف client_secret.json من Google Cloud Console")
            print("📁 ضعه في: config_grit_gold/youtube_credentials.json")

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
        
        # حفظ آخر 1000 فيديو فقط
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
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            self.gemini_client = genai.GenerativeModel(self.config.GEMINI_MODEL)
            self.logger.info("✅ Gemini مهيأ")
        except Exception as e:
            self.logger.error(f"❌ خطأ في تهيئة Gemini: {e}")
    
    def init_whisper(self):
        """تهيئة Whisper للترجمة"""
        try:
            self.whisper_model = whisper.load_model("base")
            self.logger.info("✅ Whisper مهيأ للترجمة")
        except Exception as e:
            self.logger.warning(f"⚠️ Whisper غير متوفر: {e}")
    
    def generate_viral_metadata(self, video_context: str) -> Dict:
        """توليد بيانات فيروسية للفيديو"""
        if not self.gemini_client:
            return self._get_default_metadata()
        
        try:
            prompt = self._create_viral_prompt(video_context)
            response = self.gemini_client.generate_content(prompt)
            
            # تحليل الرد
            metadata = self._parse_ai_response(response.text)
            
            # تحسين العناوين
            metadata['title'] = self._optimize_title_for_ctr(metadata['title'])
            
            self.logger.info(f"🧠 العنوان المولد: {metadata['title'][:60]}...")
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في توليد المحتوى: {e}")
            return self._get_default_metadata()
    
    def _create_viral_prompt(self, context: str) -> str:
        """إنشاء prompt فيروسي"""
        return f"""
        أنت استراتيجي محتوى لعلامة تجارية تسمى "Grit & Gold" تستهدف رواد الأعمال الشباب (18-35 سنة).
        
        السياق: {context}
        
        أنشئ حزمة فيروسية كاملة لفيديو YouTube Short:
        
        1. **العنوان** (Title):
           - باللغة الإنجليزية فقط
           - لا يزيد عن 50 حرفاً
           - يجذب الانتباه فوراً
           - يحتوي على عنصر صادم أو سري
           - أمثلة: "This 1 Habit Made Me $1M", "Why 99% Fail At Business"
        
        2. **الوصف** (Description):
           - جملتين قويتين
           - تحفيزية وعملية
           - تحتوي على دعوة للعمل
           - تنتهي بـ {self.config.BRAND_HASHTAG}
        
        3. **الوسوم** (Tags):
           - 10-15 وسم
           - مزيج بين شائع ومتخصص
           - يجب أن يتضمن: #GritAndGold #Business #Success
        
        4. **النص البرمجي** (Captions):
           - 3 جمل قصيرة من السياق
           - مثالية للعرض على الفيديو
        
        الإخراج بصيغة JSON مع المفاتيح: title, description, tags (قائمة), captions (قائمة)
        """
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """تحليل استجابة الذكاء الاصطناعي"""
        try:
            # البحث عن JSON في الرد
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # إذا فشل التحليل، إنشاء بيانات افتراضية
        return self._get_default_metadata()
    
    def _optimize_title_for_ctr(self, title: str) -> str:
        """تحسين العنوان لمعدل النقر"""
        # إضافة إيموجي في البداية
        emojis = ["🚀", "💰", "🔥", "🎯", "⚡", "💎", "👑"]
        emoji = random.choice(emojis)
        
        # تقصير إذا طويل
        if len(title) > 50:
            title = title[:47] + "..."
        
        # إضافة رقم إذا لم يكن موجوداً
        if not any(char.isdigit() for char in title):
            numbers = ["1", "3", "5", "7", "10", "100"]
            if random.random() > 0.5:
                title = title.replace("This", f"This {random.choice(numbers)}")
        
        return f"{emoji} {title}"
    
    def _get_default_metadata(self) -> Dict:
        """بيانات افتراضية إذا فشل الـ AI"""
        titles = [
            "The Truth About Making Money Online",
            "Business Secrets They Don't Want You To Know",
            "How I Went From $0 to $10k/Month",
            "The 1% Rule for Financial Freedom",
            "Stop Wasting Time - Start Making Money"
        ]
        
        return {
            'title': random.choice(titles),
            'description': f"Success requires GRIT. Join {self.config.CHANNEL_NAME} for daily business wisdom. {self.config.BRAND_HASHTAG}",
            'tags': ['Business', 'Success', 'Money', 'Entrepreneur', 'Motivation', 'GritAndGold'],
            'captions': ['You need to take action', 'Stop making excuses', 'The money is waiting for you']
        }
    
    def transcribe_audio(self, audio_path: str) -> str:
        """تحويل الصوت إلى نص"""
        if not self.whisper_model:
            return ""
        
        try:
            result = self.whisper_model.transcribe(audio_path)
            return result['text']
        except Exception as e:
            self.logger.error(f"❌ خطأ في الترجمة: {e}")
            return ""

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
            # اختيار قناة عشوائية
            channel_url = random.choice(self.config.SOURCE_CHANNELS)
            keyword = random.choice(self.config.SEARCH_KEYWORDS)
            
            self.logger.info(f"🔍 البحث في {channel_url} عن: {keyword}")
            
            # إعداد yt-dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'force_generic_extractor': False,
                'match_filter': self._create_filter(),
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # البحث في القناة
                info = ydl.extract_info(f"{channel_url}/videos", download=False)
                
                if not info or 'entries' not in info:
                    return None
                
                # تصفية الفيديوهات
                videos = []
                for entry in info['entries'][:50]:  # أول 50 فيديو
                    if self._is_good_video(entry):
                        videos.append(entry)
                
                if not videos:
                    return None
                
                # اختيار أفضل فيديو
                best_video = self._select_best_video(videos)
                
                if best_video:
                    self.logger.info(f"🎯 تم اختيار فيديو: {best_video['title'][:60]}...")
                    return best_video
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في البحث: {e}")
            return None
    
    def _create_filter(self):
        """إنشاء فلتر للبحث"""
        def match_filter(info_dict):
            # تجنب الفيديوهات المسحوبة سابقاً
            video_id = info_dict.get('id', '')
            if video_id in self.avoid_history:
                return None
            
            # تجنب الفيديوهات القصيرة جداً أو الطويلة جداً
            duration = info_dict.get('duration', 0)
            if duration < 30 or duration > 1800:  # بين 30 ثانية و30 دقيقة
                return None
            
            # تجنب الفيديوهات المنخفضة المشاهدة
            views = info_dict.get('view_count', 0)
            if views < self.config.MIN_VIEWS_THRESHOLD:
                return None
            
            # تفضيل الفيديوهات الحديثة
            upload_date = info_dict.get('upload_date', '20000101')
            try:
                date_obj = datetime.strptime(upload_date, '%Y%m%d')
                days_old = (datetime.now() - date_obj).days
                if days_old > 180:  # أقدم من 6 أشهر
                    return None
            except:
                pass
            
            return info_dict
        
        return match_filter
    
    def _is_good_video(self, video_info: Dict) -> bool:
        """فحص إذا كان الفيديو جيداً"""
        required_fields = ['id', 'title', 'duration', 'view_count']
        if not all(field in video_info for field in required_fields):
            return False
        
        # فحص العنوان (يجب أن يكون باللغة الإنجليزية وذو صلة)
        title = video_info['title'].lower()
        english_words = ['business', 'money', 'success', 'entrepreneur', 
                        'invest', 'wealth', 'rich', 'mindset', 'growth']
        
        if not any(word in title for word in english_words):
            return False
        
        # فحص المدة
        duration = video_info['duration']
        if duration < 60 or duration > 1200:  # بين دقيقة و20 دقيقة
            return False
        
        # فحص المشاهدات
        views = video_info['view_count']
        if views < self.config.MIN_VIEWS_THRESHOLD:
            return False
        
        return True
    
    def _select_best_video(self, videos: List[Dict]) -> Optional[Dict]:
        """اختيار أفضل فيديو"""
        if not videos:
            return None
        
        # حساب درجة لكل فيديو
        scored_videos = []
        for video in videos:
            score = 0
            
            # المشاهدات (40%)
            views = video.get('view_count', 0)
            score += min(views / 1000000, 1) * 40
            
            # الحداثة (30%)
            upload_date = video.get('upload_date', '20000101')
            try:
                date_obj = datetime.strptime(upload_date, '%Y%m%d')
                days_old = (datetime.now() - date_obj).days
                recency_score = max(0, 1 - (days_old / 180))  # 0-1
                score += recency_score * 30
            except:
                score += 15
            
            # المدة المثالية (20%)
            duration = video.get('duration', 0)
            ideal_duration = 300  # 5 دقائق مثالية
            duration_score = 1 - min(abs(duration - ideal_duration) / ideal_duration, 1)
            score += duration_score * 20
            
            # العشوائية (10%)
            score += random.random() * 10
            
            scored_videos.append((score, video))
        
        # اختيار الأعلى درجة
        scored_videos.sort(reverse=True, key=lambda x: x[0])
        
        return scored_videos[0][1] if scored_videos else None
    
    def download_video_segment(self, video_url: str, start_time: int = 0) -> Optional[str]:
        """تحميل مقطع من الفيديو"""
        try:
            # إنشاء اسم ملف مؤقت
            temp_dir = tempfile.mkdtemp(dir=str(self.config.TEMP_DIR))
            output_path = Path(temp_dir) / "raw_video.mp4"
            
            # حساب وقت النهاية
            end_time = start_time + self.config.SHORT_DURATION
            
            # إعداد yt-dlp للتحميل
            ydl_opts = {
                'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                'outtmpl': str(output_path.with_suffix('.%(ext)s')),
                'quiet': True,
                'no_warnings': True,
                'external_downloader': 'ffmpeg',
                'external_downloader_args': [
                    '-ss', str(start_time),  # وقت البداية
                    '-t', str(self.config.SHORT_DURATION),  # المدة
                    '-avoid_negative_ts', 'make_zero'
                ]
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            # التحقق من وجود الملف
            if output_path.exists():
                self.logger.info(f"✅ تم تحميل المقطع: {output_path}")
                return str(output_path)
            else:
                # البحث عن الملف بأي امتداد
                for ext in ['.mp4', '.mkv', '.webm', '.avi']:
                    alt_path = output_path.with_suffix(ext)
                    if alt_path.exists():
                        return str(alt_path)
            
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
        self.face_detector = self.init_face_detector()
    
    def init_face_detector(self):
        """تهيئة كاشف الوجوه"""
        try:
            mp_face = mp.solutions.face_detection
            return mp_face.FaceDetection(min_detection_confidence=0.5)
        except Exception as e:
            self.logger.warning(f"⚠️ MediaPipe غير متوفر: {e}")
            return None
    
    def process_video_for_shorts(self, input_path: str, metadata: Dict) -> Optional[str]:
        """معالجة الفيديو وتحويله لـ Shorts"""
        try:
            self.logger.info("🎬 بدء معالجة الفيديو...")
            
            # إنشاء مسار الإخراج
            output_filename = f"grit_gold_{int(time.time())}.mp4"
            output_path = self.config.OUTPUT_DIR / output_filename
            
            # 1. تحليل الفيديو
            video_info = self._analyze_video(input_path)
            
            # 2. قص الذكي مع تتبع الوجه
            cropped_path = self._smart_crop_with_face(input_path, video_info)
            if not cropped_path:
                cropped_path = self._basic_crop(input_path, video_info)
            
            # 3. إضافة الترجمات الذكية
            captioned_path = self._add_captions(cropped_path, metadata.get('captions', []))
            
            # 4. إضافة علامة مائية وتحسينات
            final_path = self._add_enhancements(captioned_path, metadata)
            
            # 5. التحقق من المدة النهائية
            self._ensure_short_duration(final_path)
            
            # 6. نقل للخارج
            shutil.move(final_path, output_path)
            
            # تنظيف الملفات المؤقتة
            self._cleanup_temp_files([input_path, cropped_path, captioned_path])
            
            self.logger.info(f"✅ الفيديو جاهز: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في المعالجة: {e}")
            return None
    
    def _analyze_video(self, video_path: str) -> Dict:
        """تحليل معلومات الفيديو"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            info = {
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
            }
            
            cap.release()
            return info
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحليل الفيديو: {e}")
            return {'width': 1920, 'height': 1080, 'fps': 30, 'duration': 60}
    
    def _smart_crop_with_face(self, video_path: str, video_info: Dict) -> Optional[str]:
        """قص ذكي مع تتبع الوجه"""
        if not self.face_detector or video_info['duration'] < 5:
            return None
        
        try:
            temp_output = Path(tempfile.mktemp(suffix='.mp4', dir=str(self.config.TEMP_DIR)))
            
            # قراءة عينات من الفيديو للكشف عن الوجه
            cap = cv2.VideoCapture(video_path)
            face_positions = []
            sample_rate = int(video_info['fps'] * 2)  # عينة كل ثانيتين
            
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_rate == 0:
                    # تحويل لـ RGB لـ MediaPipe
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = self.face_detector.process(rgb_frame)
                    
                    if results.detections:
                        for detection in results.detections:
                            bbox = detection.location_data.relative_bounding_box
                            face_positions.append({
                                'x': bbox.xmin * video_info['width'],
                                'y': bbox.ymin * video_info['height'],
                                'width': bbox.width * video_info['width'],
                                'height': bbox.height * video_info['height']
                            })
                
                frame_idx += 1
            
            cap.release()
            
            if not face_positions:
                return None
            
            # حساب متوسط موضع الوجه
            avg_x = sum(p['x'] for p in face_positions) / len(face_positions)
            avg_y = sum(p['y'] for p in face_positions) / len(face_positions)
            avg_width = sum(p['width'] for p in face_positions) / len(face_positions)
            avg_height = sum(p['height'] for p in face_positions) / len(face_positions)
            
            # حساب منطقة القص
            padding = avg_width * 0.3
            crop_x = max(0, avg_x - padding)
            crop_y = max(0, avg_y - padding)
            crop_width = min(video_info['width'] - crop_x, avg_width + padding * 2)
            crop_height = min(video_info['height'] - crop_y, avg_height + padding * 2)
            
            # ضبط النسبة لـ 9:16
            target_ratio = 9 / 16
            current_ratio = crop_width / crop_height
            
            if current_ratio > target_ratio:
                new_width = int(crop_height * target_ratio)
                crop_x += (crop_width - new_width) // 2
                crop_width = new_width
            else:
                new_height = int(crop_width / target_ratio)
                crop_y += (crop_height - new_height) // 2
                crop_height = new_height
            
            # تطبيق القص باستخدام FFmpeg
            crop_filter = f"crop={crop_width}:{crop_height}:{crop_x}:{crop_y},scale={self.config.TARGET_RESOLUTION[0]}:{self.config.TARGET_RESOLUTION[1]}"
            
            cmd = [
                'ffmpeg', '-y', '-i', video_path,
                '-vf', crop_filter,
                '-c:a', 'copy',
                str(temp_output)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            return str(temp_output)
            
        except Exception as e:
            self.logger.warning(f"⚠️ فشل القص الذكي: {e}")
            return None
    
    def _basic_crop(self, video_path: str, video_info: Dict) -> str:
        """قص أساسي"""
        temp_output = Path(tempfile.mktemp(suffix='.mp4', dir=str(self.config.TEMP_DIR)))
        
        target_width, target_height = self.config.TARGET_RESOLUTION
        input_ratio = video_info['width'] / video_info['height']
        target_ratio = target_width / target_height
        
        if input_ratio > target_ratio:
            # فيديو أوسع، قص من الجوانب
            new_width = int(video_info['height'] * target_ratio)
            crop_x = (video_info['width'] - new_width) // 2
            crop_filter = f"crop={new_width}:{video_info['height']}:{crop_x}:0"
        else:
            # فيديو أطول، قص من الأعلى/الأسفل
            new_height = int(video_info['width'] / target_ratio)
            crop_y = (video_info['height'] - new_height) // 2
            crop_filter = f"crop={video_info['width']}:{new_height}:0:{crop_y}"
        
        scale_filter = f"scale={target_width}:{target_height}"
        
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vf', f"{crop_filter},{scale_filter}",
            '-c:a', 'copy',
            str(temp_output)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        return str(temp_output)
    
    def _add_captions(self, video_path: str, captions: List[str]) -> str:
        """إضافة ترجمات ديناميكية"""
        if not captions or len(captions) < 2:
            return video_path
        
        temp_output = Path(tempfile.mktemp(suffix='.mp4', dir=str(self.config.TEMP_DIR)))
        
        try:
            # استخدام MoviePy للإضافة المتقدمة
            clip = VideoFileClip(video_path)
            duration = clip.duration
            
            # توزيع الترجمات على مدة الفيديو
            text_clips = []
            for i, caption in enumerate(captions[:3]):
                start_time = (duration / 4) * i
                end_time = start_time + (duration / 4)
                
                txt_clip = TextClip(
                    caption,
                    fontsize=70,
                    color='white',
                    font='Arial-Bold',
                    stroke_color='black',
                    stroke_width=2,
                    size=(clip.w * 0.9, None),
                    method='caption'
                )
                
                txt_clip = txt_clip.set_position(('center', 'center')).set_start(start_time).set_duration(end_time - start_time)
                text_clips.append(txt_clip)
            
            # دمج الترجمات مع الفيديو
            final_clip = CompositeVideoClip([clip] + text_clips)
            final_clip.write_videofile(str(temp_output), codec='libx264', audio_codec='aac')
            
            clip.close()
            final_clip.close()
            
            return str(temp_output)
            
        except Exception as e:
            self.logger.warning(f"⚠️ فشل إضافة الترجمات: {e}")
            return video_path
    
    def _add_enhancements(self, video_path: str, metadata: Dict) -> str:
        """إضافة تحسينات وعلامة مائية"""
        temp_output = Path(tempfile.mktemp(suffix='.mp4', dir=str(self.config.TEMP_DIR)))
        
        # إضافة علامة مائية نصية
        watermark_text = self.config.BRAND_HASHTAG
        
        cmd = [
            'ffmpeg', '-y', '-i', video_path,
            '-vf', f"drawtext=text='{watermark_text}':fontcolor=white@0.7:fontsize=30:"
                   f"x=w-text_w-20:y=h-text_h-20",
            '-c:a', 'copy',
            str(temp_output)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        return str(temp_output)
    
    def _ensure_short_duration(self, video_path: str):
        """ضمان مدة الفيديو أقل من 60 ثانية"""
        try:
            cmd = [
                'ffmpeg', '-y', '-i', video_path,
                '-t', str(self.config.SHORT_DURATION),
                '-c', 'copy',
                video_path + '_temp'
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # استبدال الملف
            os.replace(video_path + '_temp', video_path)
            
        except Exception as e:
            self.logger.warning(f"⚠️ فشل تقليل المدة: {e}")
    
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
        
        if self.config.AUTO_UPLOAD:
            self.init_youtube_service()
    
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
            self.logger.error("❌ خدمة YouTube غير مهيأة")
            return None
        
        try:
            self.logger.info(f"📤 جاري رفع الفيديو: {os.path.basename(video_path)}")
            
            # إعداد بيانات الفيديو
            body = {
                'snippet': {
                    'title': metadata.get('title', 'Grit & Gold Motivation'),
                    'description': metadata.get('description', ''),
                    'tags': metadata.get('tags', []),
                    'categoryId': '27',  # تعليم
                    'defaultLanguage': 'en'
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False,
                    'publishAt': self._calculate_publish_time()
                }
            }
            
            # رفع الفيديو
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True,
                chunksize=1024*1024
            )
            
            request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    self.logger.info(f"📊 تم رفع {int(status.progress() * 100)}%")
            
            video_id = response['id']
            video_url = f"https://youtube.com/shorts/{video_id}"
            
            self.logger.info(f"✅ تم الرفع بنجاح: {video_url}")
            
            # حذف الفيديو المحلي إذا مطلوب
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
    
    def _calculate_publish_time(self) -> Optional[str]:
        """حساب وقت النشر (مع تأخير عشوائي)"""
        if self.config.UPLOAD_SCHEDULE != "2h":
            return None
        
        now = datetime.now()
        base_interval = 2 * 3600  # ساعتين بالثواني
        
        # إضافة تأخير عشوائي (±10 دقائق)
        random_delay = random.randint(*self.config.RANDOM_DELAY_RANGE)
        next_upload = now + timedelta(seconds=base_interval + random_delay)
        
        return next_upload.isoformat() + 'Z'

# ==================== المحرك الرئيسي ====================
class GritGoldFactory:
    """المصنع الرئيسي لإمبراطورية Grit & Gold"""
    
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
            
            # 1. البحث عن محتوى فيروسي
            self.logger.info("🔎 المرحلة 1: البحث عن محتوى فيروسي...")
            video_info = self.content_hunter.find_viral_content()
            
            if not video_info:
                self.logger.warning("⚠️ لم يتم العثور على محتوى مناسب")
                return False
            
            # 2. توليد بيانات فيروسية
            self.logger.info("🧠 المرحلة 2: توليد محتوى ذكي...")
            metadata = self.ai_engine.generate_viral_metadata(video_info['title'])
            
            # 3. تحميل المقطع
            self.logger.info("📥 المرحلة 3: تحميل المقطع...")
            video_url = f"https://youtube.com/watch?v={video_info['id']}"
            
            # اختيار وقت بداية عشوائي
            duration = video_info.get('duration', 300)
            max_start = max(0, duration - self.config.SHORT_DURATION - 60)
            start_time = random.randint(0, max_start)
            
            video_path = self.content_hunter.download_video_segment(video_url, start_time)
            
            if not video_path:
                self.logger.error("❌ فشل تحميل المقطع")
                return False
            
            # 4. معالجة الفيديو
            self.logger.info("🎬 المرحلة 4: معالجة الفيديو...")
            processed_path = self.video_processor.process_video_for_shorts(video_path, metadata)
            
            if not processed_path:
                self.logger.error("❌ فشل معالجة الفيديو")
                return False
            
            # 5. رفع الفيديو
            self.logger.info("🚀 المرحلة 5: رفع الفيديو...")
            if self.config.AUTO_UPLOAD:
                video_id = self.uploader.upload_video(processed_path, metadata)
                
                if video_id:
                    self.logger.info(f"🎉 تم إنشاء ورفع الفيديو #{self.total_videos_created + 1}")
                    self.total_videos_created += 1
                    
                    # تسجيل في قاعدة البيانات
                    self._record_video_creation(video_info, metadata, video_id)
                    
                    return True
                else:
                    self.logger.error("❌ فشل رفع الفيديو")
                    return False
            else:
                self.logger.info(f"💾 تم حفظ الفيديو في: {processed_path}")
                return True
            
        except Exception as e:
            self.logger.error(f"💥 خطأ في دورة الإنتاج: {e}")
            return False
    
    def _record_video_creation(self, source_info: Dict, metadata: Dict, youtube_id: str):
        """تسجيل إنشاء الفيديو"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'youtube_id': youtube_id,
            'source_video': source_info.get('id', ''),
            'source_title': source_info.get('title', '')[:100],
            'generated_title': metadata.get('title', ''),
            'duration': self.config.SHORT_DURATION,
            'total_videos': self.total_videos_created,
            'running_time': str(datetime.now() - self.start_time)
        }
        
        db_file = self.config.DB_DIR / "production_log.json"
        logs = []
        
        if db_file.exists():
            with open(db_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        logs.append(record)
        
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(logs[-1000:], f, indent=2, ensure_ascii=False)
    
    def run_continuous_production(self):
        """تشغيل الإنتاج المستمر"""
        self.logger.info("🏭 بدء المصنع - الإنتاج المستمر مفعل")
        self.logger.info(f"🎯 الهدف: {self.config.MAX_VIDEOS_PER_DAY} فيديو يومياً")
        
        videos_today = 0
        last_reset = datetime.now()
        
        while True:
            try:
                # التحقق إذا مر يوم جديد
                now = datetime.now()
                if now.date() > last_reset.date():
                    videos_today = 0
                    last_reset = now
                    self.logger.info("🔄 تم إعادة ضبط العداد اليومي")
                
                # التحقق إذا وصلنا للحد اليومي
                if videos_today >= self.config.MAX_VIDEOS_PER_DAY:
                    self.logger.info(f"✅ وصلنا للحد اليومي ({self.config.MAX_VIDEOS_PER_DAY})")
                    
                    # الانتظار حتى اليوم التالي
                    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=1, second=0)
                    wait_seconds = (tomorrow - now).total_seconds()
                    
                    self.logger.info(f"😴 الانتظار حتى الغد: {wait_seconds/3600:.1f} ساعة")
                    time.sleep(wait_seconds)
                    continue
                
                # تشغيل دورة إنتاج
                success = self.run_production_cycle()
                
                if success:
                    videos_today += 1
                    
                    # حساب وقت الانتظار للدورة التالية
                    base_wait = 2 * 3600  # ساعتين
                    random_delay = random.randint(*self.config.RANDOM_DELAY_RANGE)
                    total_wait = base_wait + random_delay
                    
                    wait_hours = total_wait / 3600
                    next_run = now + timedelta(seconds=total_wait)
                    
                    self.logger.info(f"⏰ الدورة القادمة بعد {wait_hours:.1f} ساعة ({next_run.strftime('%H:%M')})")
                    self.logger.info(f"📊 اليوم: {videos_today}/{self.config.MAX_VIDEOS_PER_DAY}")
                    self.logger.info(f"🏆 الإجمالي: {self.total_videos_created}")
                    
                    time.sleep(total_wait)
                else:
                    # إذا فشلت الدورة، انتظر 15 دقيقة ثم حاول مجدداً
                    self.logger.warning("🔄 فشلت الدورة، إعادة المحاولة بعد 15 دقيقة...")
                    time.sleep(900)
                    
            except KeyboardInterrupt:
                self.logger.info("⏹️ تم إيقاف المصنع يدوياً")
                break
            except Exception as e:
                self.logger.error(f"💥 خطأ غير متوقع: {e}")
                time.sleep(300)  # انتظار 5 دقائق ثم استمرار

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
    
    # التحقق من المتطلبات
    print("🔍 التحقق من المتطلبات...")
    
    # إنشاء المصنع
    factory = GritGoldFactory()
    
    # سؤال عن وضع التشغيل
    print("\n" + "="*60)
    print("🎛️  خيارات التشغيل:")
    print("1. دورة واحدة (اختبار)")
    print("2. الإنتاج المستمر (تلقائي)")
    print("3. الخروج")
    
    try:
        choice = input("\nاختر الخيار [1-3]: ").strip()
        
        if choice == "1":
            print("🔄 تشغيل دورة اختبار واحدة...")
            factory.run_production_cycle()
            
        elif choice == "2":
            print("🏭 بدء المصنع - الإنتاج التلقائي المستمر")
            print("⚠️  اضغط Ctrl+C لإيقاف المصنع")
            print("="*60)
            
            factory.run_continuous_production()
            
        else:
            print("👋 مع السلامة!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ تم إيقاف البرنامج")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        sys.exit(1)
