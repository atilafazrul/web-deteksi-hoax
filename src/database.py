import os
import json
import pymysql
from datetime import datetime

# Database Configuration with Environment Variable support
DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "db_deteksi_hoax")
DB_PORT = int(os.environ.get("DB_PORT", 3306))

def get_connection(include_db=True):
    """Obtain a PyMySQL connection with dict cursor."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME if include_db else None,
        port=DB_PORT,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def init_database():
    """Create database and tables if they do not exist."""
    try:
        # 1. Connect without database to ensure DB exists
        conn = get_connection(include_db=False)
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.close()

        # 2. Connect with database and create schema
        conn = get_connection(include_db=True)
        with conn.cursor() as cursor:
            # Table: articles (hasil scan berita)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS `articles` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `url` VARCHAR(1000) NULL,
                `domain` VARCHAR(255) NULL,
                `site_name` VARCHAR(255) NULL,
                `title` VARCHAR(500) NOT NULL,
                `author` VARCHAR(255) NULL,
                `publish_date` VARCHAR(100) NULL,
                `image_url` VARCHAR(1000) NULL,
                `full_text` LONGTEXT NOT NULL,
                `verdict` VARCHAR(20) NOT NULL,
                `confidence` FLOAT NOT NULL,
                `prob_hoax` FLOAT NOT NULL,
                `prob_valid` FLOAT NOT NULL,
                `total_sentences` INT NOT NULL,
                `high_risk_sentences` INT NOT NULL,
                `medium_risk_sentences` INT NOT NULL,
                `low_risk_sentences` INT NOT NULL,
                `top_hoax_words` JSON NULL,
                `top_valid_words` JSON NULL,
                `ai_explanation` TEXT NULL,
                `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)

            # Table: article_sentences (detail per kalimat)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS `article_sentences` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `article_id` INT NOT NULL,
                `sentence_index` INT NOT NULL,
                `sentence_text` TEXT NOT NULL,
                `prob_hoax` FLOAT NOT NULL,
                `prob_valid` FLOAT NOT NULL,
                `risk_tier` VARCHAR(20) NOT NULL,
                `trigger_words` JSON NULL,
                `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)

        conn.close()
        print(f"[MySQL] Database `{DB_NAME}` dan tabel siap digunakan.")
        return True
    except Exception as e:
        print(f"[MySQL Error] Gagal inisialisasi database: {e}")
        return False

def save_analysis(analysis_data: dict) -> int:
    """Save an analysis result and its sentences into MySQL. Returns inserted article_id."""
    conn = get_connection(include_db=True)
    try:
        meta = analysis_data.get("metadata", {})
        stats = analysis_data.get("stats", {})

        with conn.cursor() as cursor:
            sql_article = """
            INSERT INTO `articles` (
                `url`, `domain`, `site_name`, `title`, `author`, `publish_date`, `image_url`,
                `full_text`, `verdict`, `confidence`, `prob_hoax`, `prob_valid`,
                `total_sentences`, `high_risk_sentences`, `medium_risk_sentences`, `low_risk_sentences`,
                `top_hoax_words`, `top_valid_words`, `ai_explanation`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Reconstruct full text from sentences or metadata
            full_text = " ".join([s["text"] for s in analysis_data.get("sentences", [])])

            cursor.execute(sql_article, (
                meta.get("url"),
                meta.get("domain"),
                meta.get("site_name"),
                analysis_data.get("title", "Berita Tanpa Judul")[:500],
                meta.get("author"),
                meta.get("date"),
                meta.get("image"),
                full_text,
                analysis_data.get("verdict"),
                analysis_data.get("confidence"),
                analysis_data.get("prob_hoax"),
                analysis_data.get("prob_valid"),
                stats.get("total_sentences", 0),
                stats.get("high_risk_sentences", 0),
                stats.get("medium_risk_sentences", 0),
                stats.get("low_risk_sentences", 0),
                json.dumps(analysis_data.get("top_hoax_words", [])),
                json.dumps(analysis_data.get("top_valid_words", [])),
                analysis_data.get("ai_explanation")
            ))
            article_id = cursor.lastrowid

            # Insert individual sentences
            sql_sentence = """
            INSERT INTO `article_sentences` (
                `article_id`, `sentence_index`, `sentence_text`,
                `prob_hoax`, `prob_valid`, `risk_tier`, `trigger_words`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            for s in analysis_data.get("sentences", []):
                cursor.execute(sql_sentence, (
                    article_id,
                    s.get("sentence_index"),
                    s.get("text"),
                    s.get("prob_hoax"),
                    s.get("prob_valid"),
                    s.get("risk_tier"),
                    json.dumps(s.get("top_hoax_triggers", []))
                ))

        return article_id
    finally:
        conn.close()

def get_recent_history(limit=20):
    """Retrieve recent scan history from MySQL."""
    conn = get_connection(include_db=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT id, url, domain, title, author, publish_date, image_url,
                   verdict, confidence, prob_hoax, prob_valid,
                   total_sentences, high_risk_sentences, medium_risk_sentences, low_risk_sentences,
                   created_at
            FROM `articles`
            ORDER BY id DESC
            LIMIT %s
            """, (limit,))
            rows = cursor.fetchall()
            # Format datetime to string for JSON serialization
            for r in rows:
                if r.get("created_at"):
                    r["created_at"] = r["created_at"].strftime("%d %b %Y, %H:%M WIB")
            return rows
    finally:
        conn.close()

def get_article_detail(article_id: int):
    """Retrieve full article detail and its sentences from MySQL."""
    conn = get_connection(include_db=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM `articles` WHERE id = %s", (article_id,))
            article = cursor.fetchone()
            if not article:
                return None

            cursor.execute("""
            SELECT sentence_index, sentence_text as text, prob_hoax, prob_valid, risk_tier, trigger_words
            FROM `article_sentences`
            WHERE article_id = %s
            ORDER BY sentence_index ASC
            """, (article_id,))
            sentences = cursor.fetchall()

            for s in sentences:
                if isinstance(s.get("trigger_words"), str):
                    try:
                        s["top_hoax_triggers"] = json.loads(s["trigger_words"])
                    except Exception:
                        s["top_hoax_triggers"] = []
                else:
                    s["top_hoax_triggers"] = s.get("trigger_words") or []

            if isinstance(article.get("top_hoax_words"), str):
                try: article["top_hoax_words"] = json.loads(article["top_hoax_words"])
                except Exception: article["top_hoax_words"] = []

            if isinstance(article.get("top_valid_words"), str):
                try: article["top_valid_words"] = json.loads(article["top_valid_words"])
                except Exception: article["top_valid_words"] = []

            if article.get("created_at"):
                article["created_at"] = article["created_at"].strftime("%d %b %Y, %H:%M WIB")

            article["sentences"] = sentences
            return article
    finally:
        conn.close()

def delete_article(article_id: int):
    """Delete an article and its sentences from MySQL."""
    conn = get_connection(include_db=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM `articles` WHERE id = %s", (article_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()

def get_dashboard_stats():
    """Calculate aggregate statistics from MySQL."""
    conn = get_connection(include_db=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT 
                COUNT(*) as total_scans,
                SUM(CASE WHEN verdict = 'HOAX' THEN 1 ELSE 0 END) as total_hoax,
                SUM(CASE WHEN verdict = 'VALID' THEN 1 ELSE 0 END) as total_valid,
                AVG(confidence) as avg_confidence
            FROM `articles`
            """)
            stats = cursor.fetchone() or {}
            
            # Top domains scanned
            cursor.execute("""
            SELECT domain, COUNT(*) as count, SUM(CASE WHEN verdict = 'HOAX' THEN 1 ELSE 0 END) as hoax_count
            FROM `articles`
            WHERE domain IS NOT NULL AND domain != ''
            GROUP BY domain
            ORDER BY count DESC
            LIMIT 5
            """)
            top_domains = cursor.fetchall()

            return {
                "total_scans": int(stats.get("total_scans") or 0),
                "total_hoax": int(stats.get("total_hoax") or 0),
                "total_valid": int(stats.get("total_valid") or 0),
                "avg_confidence": round(float(stats.get("avg_confidence") or 0), 1),
                "top_domains": [
                    {"domain": d["domain"], "count": int(d["count"]), "hoax_count": int(d["hoax_count"] or 0)}
                    for d in top_domains
                ]
            }
    finally:
        conn.close()
