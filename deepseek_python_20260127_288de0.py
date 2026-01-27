#!/usr/bin/env python3
"""
🏭 YouTube Money Printer v9.0 - GRIT & GOLD INDUSTRIAL EDITION
مخصص للسيطرة الكاملة على محتوى البزنس والشباب (قناة واحدة فقط)
"""

# ==================== 📦 المكتبات الأساسية ====================
import os
import sys
import json
import time
import random
import logging
import pickle
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ==================== 📥 تثبيت المكتبات التلقائي ====================
def install_dependencies():
    """تثبيت تلقائي للمكتبات المطلوبة"""
    required_libs = [
        "google-generativeai",
        "google-api-python-client",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "yt-dlp",
        "opencv-python",
        "numpy",
        "requests",
        "pillow",
        "moviepy"
    ]
    
    for lib in required_libs:
        try:
            __import__(lib.replace("-", "_"))
        except ImportError:
            print(f"📦 جاري تثبيت {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# ==================== ⚙️ الإعدادات الأساسية ====================
class GRIT_GOLD_CONFIG:
    """إعدادات إمبراطورية Grit & Gold"""
    
    # 🔐 الإعدادات الأساسية
    CHANNEL_NAME = "Grit & Gold"
    TARGET_LANGUAGE = "en"  # الإنجليزية للسيطرة العالمية
    NICHE = "Business | Wealth | Mindset | Success"
    
    # 🎯 القنوات المصدر (بودكاست المليارديرات)
    SOURCE_CHANNELS = [
        "https://www.youtube.com/@AlexHormozi",
        "https://www.youtube.com/@Valuetainment", 
        "https://www.youtube.com/@PatrickBetDavid",
        "https://www.youtube.com/@GaryVee",
        "https://www.youtube.com/@ImanGadzhi"
    ]
    
    # 🔥 الكلمات المفتاحية الفيروسية
    VIRAL_KEYWORDS = [
        "millionaire", "secret", "rich", "wealth", "success",
        "entrepreneur", "mindset", "business", "money", "hustle"
    ]
    
    # 📁 مسارات النظام
    BASE_DIR = Path("grit_gold_factory")
    CONFIG_DIR = BASE_DIR / "config"
    OUTPUT_DIR = BASE_DIR / "output"
    TEMP_DIR = BASE_DIR / "temp"
    LOGS_DIR = BASE_DIR / "logs"
    DATABASE = BASE_DIR / "database.json"
    
    # 📹 إعدادات الفيديو
    SHORT_DURATION = 58  # ثانية (أقل من 60 ليوتيوب شورتس)
    TARGET_RESOLUTION = (1080, 1920)  # 9:16 عمودي
    MIN_FACE_SIZE = 0.3  # الحد الأدنى لحجم الوجه في الإطار
    FPS = 30  # إطارات في الثانية
    
    # ⚡ إعدادات الأداء
    MAX_RETRIES = 3
    DELAY_BETWEEN_VIDEOS = random.randint(6600, 7800)  # 110-130 دقيقة
    MAX_VIDEOS_PER_DAY = 12  # فيديو كل ساعتين تقريباً
    
    # 🎨 إعدادات التصميم
    BRAND_COLORS = {
        "primary": "#FFD700",  # ذهبي
        "secondary": "#000000",  # أسود
        "accent": "#C0C0C0"  # فضي
    }
    
    # 🔗 روابط العلامة التجارية
    BRAND_LINKS = {
        "website": "https://gritandgold.com",
        "instagram": "@gritandgold",
        "tiktok": "@gritandgold"
    }

# ==================== 🧠 محرك الذكاء الاصطناعي ====================
class ViralAIContentEngine:
    """محرك الذكاء الاصطناعي لتوليد محتوى فيروسي"""
    
    def __init__(self):
        try:
            import google.generativeai as genai
            self.genai = genai
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("❌ لم يتم تعيين GEMINI_API_KEY")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini AI مهيأ")
        except Exception as e:
            print(f"⚠️ تحذير: {e}")
            self.model = None
    
    def generate_viral_title(self, video_context: str) -> str:
        """توليد عنوان فيروسي يجذب النقرات"""
        if not self.model:
            return self._fallback_title(video_context)
        
        prompt = f"""
        You are a viral YouTube content creator for "Grit & Gold" channel.
        Create a SHOCKING title for a business/motivation short video.
        
        Context: {video_context[:200]}
        
        Requirements:
        1. Must be in English
        2. Maximum 60 characters
        3. Use curiosity gaps
        4. Add 1-2 relevant emojis
        5. Make it controversial but professional
        6. Target young entrepreneurs (18-35)
        
        Examples of good titles:
        - "This 1 Habit Made Me $1M at 25 🔥"
        - "Why 99% of People Stay Poor 😳"
        - "The Business Secret They Don't Teach in School 💰"
        
        Generate ONLY the title, nothing else.
        """
        
        try:
            response = self.model.generate_content(prompt)
            title = response.text.strip().replace('"', '')
            return title if len(title) > 10 else self._fallback_title(video_context)
        except:
            return self._fallback_title(video_context)
    
    def generate_viral_description(self, title: str) -> str:
        """توليد وصف فيروسي"""
        if not self.model:
            return self._fallback_description()
        
        prompt = f"""
        Generate a viral YouTube description for this title: "{title}"
        
        Requirements:
        1. First line: Call to action (Subscribe & Like)
        2. Second line: Value proposition
        3. Third line: Brand promotion
        4. Hashtags: #GritAndGold #Business #Wealth #Success #Entrepreneur #Shorts
        5. Add website link
        6. Keep under 300 characters
        
        Format:
        [Call to action]
        [Value proposition]
        [Brand promotion]
        [Hashtags]
        [Website]
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return self._fallback_description()
    
    def generate_viral_tags(self, title: str) -> List[str]:
        """توليد وسوم فيروسية"""
        base_tags = [
            "gritandgold", "business", "wealth", "success",
            "entrepreneur", "money", "mindset", "motivation",
            "shorts", "viral", "millionaire", "hustle"
        ]
        
        # استخراج كلمات مفتاحية من العنوان
        words = title.lower().split()
        keyword_tags = [word for word in words if word.isalpha() and len(word) > 3]
        
        # دمج وترتيب
        all_tags = list(set(base_tags + keyword_tags[:8]))
        return all_tags[:20]  # الحد الأقصى لليوتيوب
    
    def _fallback_title(self, context: str) -> str:
        """عنوان احتياطي إذا فشل الذكاء الاصطناعي"""
        templates = [
            "The {adj} Truth About {topic} 💰",
            "Why {percentage}% of People {action} 😳",
            "How I Made ${amount} at Age {age} 🔥",
            "The {adj} Business Secret Nobody Tells You 🚀",
            "{number} Things Millionaires Do Differently 💎"
        ]
        
        template = random.choice(templates)
        adj = random.choice(["Shocking", "Hidden", "Brutal", "Real", "Painful"])
        topic = random.choice(["Wealth", "Success", "Money", "Business"])
        percentage = random.choice(["95", "99", "90", "98"])
        action = random.choice(["Stay Poor", "Fail", "Give Up", "Quit"])
        amount = random.choice(["100K", "500K", "1M", "10M"])
        age = random.choice(["21", "25", "30", "35"])
        number = random.choice(["3", "5", "7", "10"])
        
        return template.format(
            adj=adj, topic=topic, percentage=percentage,
            action=action, amount=amount, age=age, number=number
        )
    
    def _fallback_description(self) -> str:
        """وصف احتياطي"""
        return """🔥 LIKE & SUBSCRIBE for daily wealth secrets!
💎 Join Grit & Gold for exclusive business content!
🚀 Follow for more: @gritandgold

#GritAndGold #Business #Wealth #Success #Entrepreneur #Money #Mindset #Shorts

👉 https://gritandgold.com"""

# ==================== 📹 محرك معالجة الفيديو ====================
class VideoFactory:
    """مصنع الفيديوهات الفيروسية"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.temp_files = []
    
    def _setup_logger(self):
        """إعداد نظام التسجيل"""
        GRIT_GOLD_CONFIG.LOGS_DIR.mkdir(exist_ok=True)
        
        logger = logging.getLogger("GritGoldFactory")
        logger.setLevel(logging.INFO)
        
        # ملف السجلات
        file_handler = logging.FileHandler(
            GRIT_GOLD_CONFIG.LOGS_DIR / f"factory_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        ))
        logger.addHandler(file_handler)
        
        # وحدة التحكم
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(levelname)s: %(message)s'
        ))
        logger.addHandler(console_handler)
        
        return logger
    
    def download_source_video(self) -> Optional[Path]:
        """تحميل فيديو من القنوات المصدر"""
        self.logger.info("🎯 جاري البحث عن محتوى فيروسي...")
        
        source = random.choice(GRIT_GOLD_CONFIG.SOURCE_CHANNELS)
        temp_path = GRIT_GOLD_CONFIG.TEMP_DIR / f"source_{int(time.time())}.mp4"
        
        try:
            # استخدام yt-dlp لتحميل أفضل فيديو قصير
            import yt_dlp
            
            ydl_opts = {
                'format': 'best[height<=1080]',
                'outtmpl': str(temp_path.with_suffix('.%(ext)s')),
                'quiet': True,
                'no_warnings': True,
                'max_downloads': 1,
                'playlist_items': '1',  # أول فيديو فقط
                'match_filter': self._filter_videos,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(source + "/videos", download=True)
                
                if info and 'entries' in info:
                    video_info = info['entries'][0]
                    self.logger.info(f"✅ تم تحميل: {video_info.get('title', 'Unknown')[:50]}")
                    
                    # التأكد من الملف
                    if temp_path.exists():
                        self.temp_files.append(temp_path)
                        return temp_path
        
        except Exception as e:
            self.logger.error(f"❌ خطأ في التحميل: {e}")
        
        return None
    
    def _filter_videos(self, info_dict):
        """تصفية الفيديوهات المناسبة"""
        # استبعاد الفيديوهات الطويلة جداً
        if info_dict.get('duration', 9999) > 600:  # أكثر من 10 دقائق
            return "الفيديو طويل جداً"
        
        # استبعاد الفيديوهات القصيرة جداً
        if info_dict.get('duration', 0) < 30:  # أقل من 30 ثانية
            return "الفيديو قصير جداً"
        
        # تفضيل الفيديوهات ذات المشاهدات العالية
        if info_dict.get('view_count', 0) < 10000:
            return "المشاهدات قليلة"
        
        return None
    
    def create_viral_short(self, source_path: Path) -> Optional[Path]:
        """تحويل الفيديو إلى شورت فيروسي"""
        self.logger.info("✂️ جاري إنشاء شورت فيروسي...")
        
        output_path = GRIT_GOLD_CONFIG.OUTPUT_DIR / f"grit_gold_{int(time.time())}.mp4"
        
        try:
            # 1. اكتشاف الوجه تلقائياً
            face_crop = self._detect_and_crop_face(source_path)
            
            # 2. تحويل إلى 9:16
            if face_crop:
                crop_filter = face_crop
            else:
                # إذا لم يتم اكتشاف وجه، قص المنتصف
                crop_filter = "crop=ih*(9/16):ih"
            
            # 3. إضافة تأثيرات فيروسية
            ffmpeg_cmd = [
                'ffmpeg', '-y', '-i', str(source_path),
                '-vf', f'{crop_filter},scale=1080:1920',
                '-t', str(GRIT_GOLD_CONFIG.SHORT_DURATION),
                '-c:v', 'libx264', '-preset', 'fast',
                '-crf', '23', '-r', '30',
                '-c:a', 'aac', '-b:a', '128k',
                '-pix_fmt', 'yuv420p',
                str(output_path)
            ]
            
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 دقائق كحد أقصى
            )
            
            if result.returncode == 0:
                self.logger.info(f"✅ تم إنشاء الشورت: {output_path.name}")
                self.temp_files.append(output_path)
                return output_path
            else:
                self.logger.error(f"❌ خطأ في FFmpeg: {result.stderr[:200]}")
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في معالجة الفيديو: {e}")
        
        return None
    
    def _detect_and_crop_face(self, video_path: Path) -> Optional[str]:
        """اكتشاف الوجه وقص الفيديو حوله"""
        try:
            import cv2
            import numpy as np
            
            # تحميل مصنف الوجه
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # فتح الفيديو
            cap = cv2.VideoCapture(str(video_path))
            
            # أخذ عينة من الإطارات
            face_positions = []
            sample_rate = 30  # إطار كل 30 إطار
            
            for i in range(0, 100, sample_rate):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # تحويل إلى تدرج الرمادي
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # اكتشاف الوجه
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                for (x, y, w, h) in faces:
                    face_positions.append({
                        'x': x, 'y': y, 'w': w, 'h': h,
                        'frame_width': frame.shape[1],
                        'frame_height': frame.shape[0]
                    })
            
            cap.release()
            
            if not face_positions:
                return None
            
            # حساب متوسط موضع الوجه
            avg_x = sum(f['x'] for f in face_positions) / len(face_positions)
            avg_y = sum(f['y'] for f in face_positions) / len(face_positions)
            avg_w = sum(f['w'] for f in face_positions) / len(face_positions)
            avg_h = sum(f['h'] for f in face_positions) / len(face_positions)
            
            # إضافة هامش حول الوجه
            margin = avg_w * 0.5
            crop_x = max(0, avg_x - margin)
            crop_y = max(0, avg_y - margin)
            crop_w = min(avg_w + margin * 2, face_positions[0]['frame_width'] - crop_x)
            crop_h = min(avg_h + margin * 2, face_positions[0]['frame_height'] - crop_y)
            
            # تحويل النسبة إلى 9:16
            target_ratio = 9 / 16
            current_ratio = crop_w / crop_h
            
            if current_ratio > target_ratio:
                # واسع جداً، تقليل العرض
                new_width = int(crop_h * target_ratio)
                crop_x += (crop_w - new_width) // 2
                crop_w = new_width
            else:
                # طويل جداً، تقليل الارتفاع
                new_height = int(crop_w / target_ratio)
                crop_y += (crop_h - new_height) // 2
                crop_h = new_height
            
            return f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y}"
            
        except Exception as e:
            self.logger.warning(f"⚠️ فشل اكتشاف الوجه: {e}")
            return None
    
    def add_brand_overlay(self, video_path: Path) -> Optional[Path]:
        """إضافة علامة Grit & Gold التجارية"""
        self.logger.info("🎨 جاري إضافة العلامة التجارية...")
        
        branded_path = GRIT_GOLD_CONFIG.OUTPUT_DIR / f"branded_{video_path.name}"
        
        try:
            # إنشاء نص العلامة التجارية
            brand_text = "Grit & Gold"
            
            # إضافة النص باستخدام FFmpeg
            ffmpeg_cmd = [
                'ffmpeg', '-y', '-i', str(video_path),
                '-vf', f"drawtext=text='{brand_text}':"
                       f"fontcolor=white:fontsize=24:"
                       f"box=1:boxcolor=black@0.5:boxborderw=5:"
                       f"x=w-text_w-20:y=20",
                '-c:a', 'copy',
                str(branded_path)
            ]
            
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.logger.info("✅ تمت إضافة العلامة التجارية")
                self.temp_files.append(branded_path)
                return branded_path
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في إضافة العلامة: {e}")
        
        return video_path  # الرجوع للفيديو الأصلي إذا فشل
    
    def cleanup(self):
        """تنظيف الملفات المؤقتة"""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except:
                pass
        self.temp_files.clear()

# ==================== 📤 محرك الرفع لليوتيوب ====================
class YouTubeAutoUploader:
    """الرفع التلقائي لليوتيوب"""
    
    def __init__(self):
        self.service = None
        self.credentials_file = GRIT_GOLD_CONFIG.CONFIG_DIR / "client_secret.json"
        self.token_file = GRIT_GOLD_CONFIG.CONFIG_DIR / "token.pickle"
        
    def authenticate(self) -> bool:
        """المصادقة مع يوتيوب API"""
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            
            SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
            creds = None
            
            # تحميل التوكن الموجود
            if self.token_file.exists():
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # إذا لم تكن هناك بيانات مصادقة أو انتهت صلاحيتها
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.credentials_file.exists():
                        print("❌ ملف client_secret.json غير موجود")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # حفظ التوكن للمرة القادمة
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            # بناء الخدمة
            from googleapiclient.discovery import build
            self.service = build("youtube", "v3", credentials=creds)
            print("✅ تم المصادقة مع يوتيوب API")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في المصادقة: {e}")
            return False
    
    def upload_video(self, video_path: Path, metadata: Dict) -> Optional[str]:
        """رفع الفيديو لليوتيوب"""
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            from googleapiclient.http import MediaFileUpload
            
            # إعداد بيانات الفيديو
            body = {
                "snippet": {
                    "title": metadata.get("title", "Grit & Gold Motivation"),
                    "description": metadata.get("description", ""),
                    "tags": metadata.get("tags", []),
                    "categoryId": "22"  # People & Blogs
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            }
            
            # رفع الوسائط
            media = MediaFileUpload(
                str(video_path),
                mimetype='video/mp4',
                resumable=True,
                chunksize=1024*1024
            )
            
            print("🚀 جاري رفع الفيديو...")
            request = self.service.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"📤 التقدم: {int(status.progress() * 100)}%")
            
            video_id = response["id"]
            print(f"✅ تم الرفع بنجاح! ID: {video_id}")
            
            # تسجيل في قاعدة البيانات
            self._log_upload(video_id, metadata)
            
            return video_id
            
        except Exception as e:
            print(f"❌ خطأ في الرفع: {e}")
            return None
    
    def _log_upload(self, video_id: str, metadata: Dict):
        """تسجيل الفيديو المرفوع في قاعدة البيانات"""
        try:
            if GRIT_GOLD_CONFIG.DATABASE.exists():
                with open(GRIT_GOLD_CONFIG.DATABASE, 'r') as f:
                    database = json.load(f)
            else:
                database = {"uploads": []}
            
            database["uploads"].append({
                "video_id": video_id,
                "title": metadata.get("title", ""),
                "uploaded_at": datetime.now().isoformat(),
                "channel": GRIT_GOLD_CONFIG.CHANNEL_NAME
            })
            
            # حفظ آخر 1000 فيديو فقط
            if len(database["uploads"]) > 1000:
                database["uploads"] = database["uploads"][-1000:]
            
            with open(GRIT_GOLD_CONFIG.DATABASE, 'w') as f:
                json.dump(database, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ خطأ في التسجيل: {e}")

# ==================== 🏭 الماكينة الرئيسية ====================
class MoneyPrinter:
    """الماكينة الرئيسية - مطبعة النقود"""
    
    def __init__(self):
        self.setup_directories()
        self.ai_engine = ViralAIContentEngine()
        self.video_factory = VideoFactory()
        self.uploader = YouTubeAutoUploader()
        self.videos_today = 0
        
    def setup_directories(self):
        """إعداد المجلدات الأساسية"""
        for directory in [
            GRIT_GOLD_CONFIG.BASE_DIR,
            GRIT_GOLD_CONFIG.CONFIG_DIR,
            GRIT_GOLD_CONFIG.OUTPUT_DIR,
            GRIT_GOLD_CONFIG.TEMP_DIR,
            GRIT_GOLD_CONFIG.LOGS_DIR
        ]:
            directory.mkdir(exist_ok=True)
    
    def get_video_context(self, video_path: Path) -> str:
        """استخراج سياق الفيديو (للاستخدام المستقبلي مع Whisper)"""
        # يمكن دمج Whisper هنا لتحويل الصوت إلى نص
        return random.choice([
            "Business secrets from top entrepreneurs",
            "Millionaire mindset tips for young hustlers",
            "Wealth building strategies that actually work",
            "Entrepreneur motivation for the next generation"
        ])
    
    def produce_viral_video(self) -> bool:
        """إنتاج فيديو فيروسي كامل"""
        print("\n" + "="*60)
        print(f"🏭 جولة إنتاج جديدة | {datetime.now().strftime('%H:%M')}")
        print("="*60)
        
        try:
            # 1. تحميل الفيديو المصدر
            source_video = self.video_factory.download_source_video()
            if not source_video:
                print("❌ فشل في تحميل الفيديو المصدر")
                return False
            
            # 2. استخراج السياق
            context = self.get_video_context(source_video)
            
            # 3. توليد محتوى فيروسي
            print("🧠 جاري توليد محتوى فيروسي...")
            title = self.ai_engine.generate_viral_title(context)
            description = self.ai_engine.generate_viral_description(title)
            tags = self.ai_engine.generate_viral_tags(title)
            
            print(f"📝 العنوان: {title}")
            
            # 4. إنشاء الشورت
            short_video = self.video_factory.create_viral_short(source_video)
            if not short_video:
                print("❌ فشل في إنشاء الشورت")
                return False
            
            # 5. إضافة العلامة التجارية
            branded_video = self.video_factory.add_brand_overlay(short_video)
            
            # 6. رفع الفيديو
            metadata = {
                "title": title,
                "description": description,
                "tags": tags
            }
            
            video_id = self.uploader.upload_video(branded_video, metadata)
            
            if video_id:
                print(f"✅ تم إنتاج ورفع الفيديو بنجاح!")
                self.videos_today += 1
                
                # 7. تنظيف الملفات المؤقتة
                self.video_factory.cleanup()
                
                # 8. تأخير عشوائي للجولة القادمة
                delay = random.randint(6600, 7800)  # 110-130 دقيقة
                print(f"😴 النوم لمدة {delay//60} دقيقة للجولة القادمة...")
                
                return True
            else:
                print("❌ فشل في رفع الفيديو")
                return False
                
        except Exception as e:
            print(f"💥 خطأ غير متوقع: {e}")
            return False
    
    def run(self, max_videos: int = None):
        """تشغيل الماكينة"""
        print("""
╔══════════════════════════════════════════════════════════════════════╗
║                🏭 GRIT & GOLD MONEY PRINTER v9.0                     ║
║                Industrial Business Content Factory                   ║
║                Target: One Channel Domination                        ║
╚══════════════════════════════════════════════════════════════════════╝
        """)
        
        if max_videos is None:
            max_videos = GRIT_GOLD_CONFIG.MAX_VIDEOS_PER_DAY
        
        successful_videos = 0
        attempts = 0
        
        while successful_videos < max_videos and attempts < max_videos * 2:
            attempts += 1
            
            if self.produce_viral_video():
                successful_videos += 1
            
            # تأخير بين المحاولات
            if successful_videos < max_videos:
                delay = random.randint(300, 900)  # 5-15 دقيقة
                time.sleep(delay)
        
        print(f"\n🎉 اكتملت جولة الإنتاج اليومية!")
        print(f"✅ نجح: {successful_videos} فيديو | ❌ فشل: {attempts - successful_videos}")

# ==================== 🚀 نقطة الدخول ====================
def main():
    """الدالة الرئيسية"""
    
    # التحقق من المكتبات
    install_dependencies()
    
    # التحقق من وجود ملفات المصادقة
    config_dir = GRIT_GOLD_CONFIG.CONFIG_DIR
    if not (config_dir / "client_secret.json").exists():
        print("""
❌ ملف client_secret.json غير موجود!
        
لرفع الفيديوهات تلقائياً، تحتاج إلى:
1. الذهاب إلى: https://console.cloud.google.com
2. إنشاء مشروع جديد
3. تفعيل YouTube Data API v3
4. إنشاء OAuth 2.0 credentials
5. تحميل ملف client_secret.json
6. وضعه في مجلد: {config_dir}
        
بدون هذا الملف، سيعمل الكود على إنشاء الفيديوهات فقط دون رفعها.
        """)
    
    # تشغيل الماكينة
    printer = MoneyPrinter()
    
    # اختيار وضع التشغيل
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            print("🧪 وضع الاختبار: إنشاء فيديو واحد فقط")
            printer.produce_viral_video()
        elif sys.argv[1].isdigit():
            count = int(sys.argv[1])
            print(f"🔧 وضع مخصص: إنشاء {count} فيديوهات")
            printer.run(count)
        else:
            printer.run()
    else:
        # التشغيل العادي (يومي)
        printer.run()

if __name__ == "__main__":
    main()
        
