import os
import sys

# Windows Winsock Fix
if sys.platform == "win32":
    system_root = os.environ.get("SystemRoot") or os.environ.get("SYSTEMROOT") or "C:\\Windows"
    os.environ["SystemRoot"] = system_root
    os.environ["SYSTEMROOT"] = system_root

import re
import json
import joblib
import numpy as np
from src.text_preprocessing import clean_text_id
from src.news_extractor import extract_article_from_url, split_into_sentences
from src.models.generative_reasoner import GenerativeFactChecker

def detect_language(text: str) -> str:
    """Detect if text is primarily Indonesian ('id') or Foreign / English ('en')."""
    if not text:
        return 'id'
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    if not words:
        return 'id'

    id_markers = {
        'yang', 'di', 'dan', 'ini', 'itu', 'untuk', 'dari', 'dalam', 'tidak', 'pada', 
        'adalah', 'ke', 'dengan', 'saya', 'kita', 'mereka', 'ada', 'akan', 'oleh', 
        'telah', 'saat', 'juga', 'bisa', 'karena', 'ia', 'atau', 'lebih', 'sudah'
    }
    en_markers = {
        'the', 'of', 'and', 'to', 'in', 'is', 'that', 'for', 'on', 'with', 
        'as', 'by', 'at', 'from', 'this', 'was', 'are', 'it', 'have', 'be',
        'has', 'his', 'said', 'after', 'who', 'he', 'they', 'which', 'an'
    }

    id_count = sum(1 for w in words if w in id_markers)
    en_count = sum(1 for w in words if w in en_markers)
    return 'en' if en_count > id_count and en_count >= 3 else 'id'

class HoaxDetectionService:
    def __init__(self, model_path="saved_models/svm_tfidf_pipeline.joblib"):
        self.model_path = model_path
        self.pipeline = None
        self.feature_names = None
        self.coef = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file {self.model_path} not found. Please train SVM first.")
        
        self.pipeline = joblib.load(self.model_path)
        tfidf = self.pipeline.named_steps['tfidf']
        clf = self.pipeline.named_steps['clf']
        
        self.feature_names = np.array(tfidf.get_feature_names_out())
        
        # Get LinearSVC coefficients
        if hasattr(clf, 'calibrated_classifiers_'):
            base_clf = clf.calibrated_classifiers_[0].estimator
        else:
            base_clf = clf
            
        if hasattr(base_clf, 'coef_'):
            self.coef = base_clf.coef_[0]
        else:
            self.coef = np.zeros(len(self.feature_names))

    def analyze_text(self, text: str, title: str = "", metadata: dict = None, api_key: str = None) -> dict:
        """
        Analyze a news text:
        - Overall Hoax / Valid classification & confidence
        - Sentence-level classification and risk rating
        - Word / N-Gram attributions (which words trigger hoax vs valid)
        - Highlighted HTML reconstruction
        """
        if not text or not text.strip():
            return {"status": "error", "error_msg": "Teks berita tidak boleh kosong."}

        combined_for_pred = f"{title}. {text}" if title else text

        # Check language: if English/foreign, route to Gemini multilingual verifier
        lang = detect_language(combined_for_pred)
        if lang == "en":
            try:
                res = self._analyze_multilingual_with_gemini(text, title=title, metadata=metadata, api_key=api_key)
                if res and res.get("status") == "success":
                    return res
            except Exception as e:
                print(f"[WARN] Gemini multilingual check fallback to local SVM: {e}", file=sys.stderr)

        # 1. Overall prediction
        combined_for_pred = f"{title}. {text}" if title else text
        probs = self.pipeline.predict_proba([combined_for_pred])[0]
        prob_valid = float(probs[0])
        prob_hoax = float(probs[1])
        
        is_hoax = prob_hoax >= 0.5
        label = "HOAX" if is_hoax else "VALID"
        confidence = prob_hoax if is_hoax else prob_valid

        # 2. Extract Top Contributing Words in the entire text
        top_hoax_words, top_valid_words = self._get_feature_contributions(combined_for_pred, top_k=12)

        # 3. Sentence-level analysis ("Bagian mana yang hoax")
        sentences = split_into_sentences(text)
        sentence_details = []
        high_risk_count = 0
        med_risk_count = 0
        low_risk_count = 0

        for idx, s in enumerate(sentences):
            s_clean = s.strip()
            if not s_clean:
                continue
            
            s_probs = self.pipeline.predict_proba([s_clean])[0]
            s_hoax_prob = float(s_probs[1])
            s_valid_prob = float(s_probs[0])

            # Get trigger words for this specific sentence
            s_hoax_words, s_valid_words = self._get_feature_contributions(s_clean, top_k=5)

            # Determine risk tier
            if s_hoax_prob >= 0.70:
                risk_tier = "high"
                risk_label = "Tinggi (Indikasi Kuat Hoaks)"
                badge_color = "red"
                high_risk_count += 1
            elif s_hoax_prob >= 0.45:
                risk_tier = "medium"
                risk_label = "Mencurigakan (Perlu Cek Fakta)"
                badge_color = "amber"
                med_risk_count += 1
            else:
                risk_tier = "low"
                risk_label = "Aman / Faktual"
                badge_color = "emerald"
                low_risk_count += 1

            sentence_details.append({
                "sentence_index": idx + 1,
                "text": s_clean,
                "prob_hoax": round(s_hoax_prob * 100, 1),
                "prob_valid": round(s_valid_prob * 100, 1),
                "risk_tier": risk_tier,
                "risk_label": risk_label,
                "badge_color": badge_color,
                "top_hoax_triggers": [w for w, _ in s_hoax_words],
                "top_valid_triggers": [w for w, _ in s_valid_words]
            })

        # 4. Generate highlighted HTML for interactive reader
        highlighted_html = self._build_highlighted_html(sentence_details)

        result = {
            "status": "success",
            "title": title or "Teks Berita",
            "verdict": label,
            "is_hoax": is_hoax,
            "confidence": round(confidence * 100, 1),
            "prob_hoax": round(prob_hoax * 100, 1),
            "prob_valid": round(prob_valid * 100, 1),
            "stats": {
                "total_sentences": len(sentence_details),
                "high_risk_sentences": high_risk_count,
                "medium_risk_sentences": med_risk_count,
                "low_risk_sentences": low_risk_count,
                "hoax_sentence_ratio": round((high_risk_count + med_risk_count) / max(1, len(sentence_details)) * 100, 1)
            },
            "top_hoax_words": top_hoax_words,
            "top_valid_words": top_valid_words,
            "sentences": sentence_details,
            "highlighted_html": highlighted_html,
            "metadata": metadata or {}
        }
        return result

    def analyze_url(self, url: str, api_key: str = None) -> dict:
        """Fetch article from URL, then analyze it."""
        article = extract_article_from_url(url)
        if article.get("status") == "error":
            return article

        analysis = self.analyze_text(
            text=article["full_text"],
            title=article.get("title", ""),
            metadata={
                "url": article.get("url"),
                "domain": article.get("domain"),
                "site_name": article.get("site_name"),
                "author": article.get("author"),
                "date": article.get("date"),
                "image": article.get("image")
            },
            api_key=api_key
        )
        return analysis

    def _analyze_multilingual_with_gemini(self, text: str, title: str = "", metadata: dict = None, api_key: str = None) -> dict:
        """
        Multilingual fact-checker using Gemini API.
        Used for English and international news (BBC, Reuters, AP, etc.)
        where monolingual Indonesian SVM TF-IDF is not applicable.
        """
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        from google import genai
        client = genai.Client(api_key=api_key)

        domain = (metadata.get("domain") or "").lower() if metadata else ""
        sentences = split_into_sentences(text)
        # Filter boilerplate and take up to 18 sentences for prompt
        clean_sentences = [
            s.strip() for s in sentences
            if s.strip() and not any(bp in s for bp in ["enable JavaScript", "HTML5 video", "Sign up for", "Cookie preferences"])
        ]
        sample_sentences = clean_sentences[:18]
        numbered_sentences = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sample_sentences)])

        VERIFIED_NEWS_OUTLETS = {
            "bbc.com", "bbc.co.uk", "reuters.com", "apnews.com", "dw.com",
            "theguardian.com", "aljazeera.com", "bloomberg.com", "nytimes.com",
            "washingtonpost.com", "wsj.com", "ft.com", "cnn.com", "cnbc.com",
            "abc.net.au", "france24.com", "japantimes.co.jp", "scmp.com",
            "kompas.com", "tempo.co", "antaranews.com", "detik.com", "liputan6.com",
            "merdeka.com", "republika.co.id", "tribunnews.com"
        }

        is_verified_source = any(vd in domain for vd in VERIFIED_NEWS_OUTLETS)
        is_debunk_page = any(kw in (title + " " + domain).lower() for kw in ["fact-check", "factcheck", "[salah]", "hoax check", "debunked", "false claim"])

        if is_verified_source and not is_debunk_page:
            prompt = f"""You are an expert news analyst and foreign correspondent.
This is an authentic news article published directly on the verified official domain '{domain}':
Title: {title}
Article Sentences:
{numbered_sentences}

Task:
1. Provide a clear, professional journalistic summary in Indonesian explaining the key events, real-world context, and background of this reporting.
2. Extract 3-5 key journalistic terms supporting the reporting.

Return strictly a JSON object:
{{
  "verdict": "VALID",
  "confidence": 99.0,
  "summary": "Rangkuman fakta dan konteks berita dalam Bahasa Indonesia...",
  "suspicious_sentences": [],
  "top_valid_words": [["official reporting", 0.95], ["verified news", 0.90]],
  "top_hoax_words": []
}}
"""
        elif is_debunk_page:
            prompt = f"""You are an expert fact-checking desk analyst.
This article is a published fact-check report from '{domain}' investigating viral claims:
Title: {title}
Article Sentences:
{numbered_sentences}

Task:
1. Determine the status of the viral claim being investigated (is the claim debunked as HOAX, or verified as VALID?).
2. If the viral claim being debunked is false, return verdict: "HOAX" and summarize which claims were refuted.
3. Provide an Indonesian explanation detailing the debunked facts.

Return strictly a JSON object:
{{
  "verdict": "HOAX",
  "confidence": 98.0,
  "summary": "Penjelasan hasil cek fakta resmi dalam Bahasa Indonesia...",
  "suspicious_sentences": [],
  "top_valid_words": [],
  "top_hoax_words": [["debunked claim", 0.95]]
}}
"""
        else:
            prompt = f"""You are an elite global news verifier and fact-checking analyst.
Evaluate this unverified news text or social media claim:
Publisher Domain: {domain or 'Unknown / Direct Text'}
Title: {title}
Article Sentences:
{numbered_sentences}

Task:
1. Determine if this article is VALID (credible factual journalism) or HOAX (disinformation, fabricated news, scam, conspiracy theory).
2. Rate confidence percentage (75.0 to 99.0).
3. Identify which sentence numbers (1-based index) contain false or fabricated claims.
4. Provide a clear summary in Indonesian explaining the factual basis.

Return strictly a JSON object:
{{
  "verdict": "VALID",
  "confidence": 98.0,
  "summary": "Penjelasan status fakta dalam Bahasa Indonesia...",
  "suspicious_sentences": [
    {{"index": 2, "risk": "high", "reason": "Alasan kalimat dicurigai", "triggers": ["kata kunci pemicu"]}}
  ],
  "top_valid_words": [["verified event", 0.90]],
  "top_hoax_words": [["conspiracy", 0.90]]
}}
"""
        models_to_try = ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
        response_text = None
        for m in models_to_try:
            try:
                resp = client.models.generate_content(model=m, contents=prompt)
                response_text = resp.text
                break
            except Exception:
                continue

        if not response_text:
            raise RuntimeError("Gagal menghubungi layanan verifikasi multibahasa AI.")

        # Clean JSON markdown fences
        clean_json = response_text.strip()
        if clean_json.startswith("```"):
            clean_json = re.sub(r"^```[a-zA-Z]*\n?", "", clean_json)
            clean_json = re.sub(r"\n?```$", "", clean_json)

        data = json.loads(clean_json)

        verdict = data.get("verdict", "VALID").upper()
        is_hoax = (verdict == "HOAX")
        confidence = float(data.get("confidence", 95.0))
        summary = data.get("summary", "")

        prob_hoax = confidence if is_hoax else round(100.0 - confidence, 1)
        prob_valid = round(100.0 - prob_hoax, 1)

        # Build map of suspicious sentences
        suspicious_map = {}
        for item in data.get("suspicious_sentences", []):
            idx = item.get("index")
            if idx is not None:
                suspicious_map[int(idx)] = item

        sentence_details = []
        high_risk_count = 0
        med_risk_count = 0
        low_risk_count = 0

        for idx, s in enumerate(sentences):
            s_clean = s.strip()
            if not s_clean:
                continue

            s_idx = idx + 1
            if s_idx in suspicious_map:
                s_info = suspicious_map[s_idx]
                tier = s_info.get("risk", "high")
                if tier == "high":
                    s_prob = float(s_info.get("prob_hoax", 85.0))
                    risk_label = "Tinggi (Indikasi Kuat Hoaks)"
                    badge_color = "red"
                    high_risk_count += 1
                else:
                    s_prob = float(s_info.get("prob_hoax", 55.0))
                    risk_label = "Mencurigakan (Perlu Cek Fakta)"
                    badge_color = "amber"
                    med_risk_count += 1
                s_hoax_prob = s_prob
                s_valid_prob = round(100.0 - s_hoax_prob, 1)
                triggers = s_info.get("triggers", [])
            else:
                if is_hoax:
                    s_hoax_prob = 65.0
                    s_valid_prob = 35.0
                    tier = "medium"
                    risk_label = "Mencurigakan (Bagian Narasi Hoaks)"
                    badge_color = "amber"
                    med_risk_count += 1
                else:
                    s_hoax_prob = 2.0
                    s_valid_prob = 98.0
                    tier = "low"
                    risk_label = "Aman / Faktual"
                    badge_color = "emerald"
                    low_risk_count += 1
                triggers = []

            sentence_details.append({
                "sentence_index": s_idx,
                "text": s_clean,
                "prob_hoax": s_hoax_prob,
                "prob_valid": s_valid_prob,
                "risk_tier": tier,
                "risk_label": risk_label,
                "badge_color": badge_color,
                "top_hoax_triggers": triggers,
                "top_valid_triggers": []
            })

        highlighted_html = self._build_highlighted_html(sentence_details)

        return {
            "status": "success",
            "title": title or "Artikel Berita Internasional",
            "verdict": verdict,
            "is_hoax": is_hoax,
            "confidence": confidence,
            "prob_hoax": prob_hoax,
            "prob_valid": prob_valid,
            "stats": {
                "total_sentences": len(sentence_details),
                "high_risk_sentences": high_risk_count,
                "medium_risk_sentences": med_risk_count,
                "low_risk_sentences": low_risk_count,
                "hoax_sentence_ratio": round((high_risk_count + med_risk_count) / max(1, len(sentence_details)) * 100, 1)
            },
            "top_hoax_words": data.get("top_hoax_words", []),
            "top_valid_words": data.get("top_valid_words", []),
            "sentences": sentence_details,
            "highlighted_html": highlighted_html,
            "metadata": metadata or {},
            "ai_explanation": summary,
            "language": "en",
            "language_label": "Bahasa Internasional (Diverifikasi oleh AI Global)"
        }

    def explain_with_gemini(self, text: str, predicted_label: str, confidence: float, api_key: str = None) -> str:
        checker = GenerativeFactChecker(api_key=api_key)
        return checker.explain(text, predicted_label=predicted_label, confidence=confidence / 100.0)

    def _get_feature_contributions(self, text: str, top_k: int = 10):
        """Find the words/n-grams with the strongest positive (hoax) and negative (valid) weights."""
        tfidf = self.pipeline.named_steps['tfidf']
        vec = tfidf.transform([text]).toarray()[0]
        active_indices = np.where(vec > 0)[0]
        
        if len(active_indices) == 0:
            return [], []

        contributions = []
        for i in active_indices:
            word = self.feature_names[i]
            score = float(self.coef[i] * vec[i])
            contributions.append((word, score))

        # Positive = pushing to Hoax, Negative = pushing to Valid
        hoax_words = sorted([(w, round(s, 3)) for w, s in contributions if s > 0], key=lambda x: x[1], reverse=True)[:top_k]
        valid_words = sorted([(w, round(abs(s), 3)) for w, s in contributions if s < 0], key=lambda x: x[1], reverse=True)[:top_k]

        return hoax_words, valid_words

    def _build_highlighted_html(self, sentence_details: list) -> str:
        """Wrap each sentence in an interactive HTML span with data attributes and CSS classes."""
        html_parts = []
        for s in sentence_details:
            tier = s["risk_tier"]
            prob = s["prob_hoax"]
            idx = s["sentence_index"]
            triggers = ", ".join(s["top_hoax_triggers"][:3]) if s["top_hoax_triggers"] else "-"
            
            # Escape HTML in text
            escaped_text = (
                s["text"]
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )

            span = (
                f'<span class="sentence-mark tier-{tier}" '
                f'data-index="{idx}" '
                f'data-tier="{tier}" '
                f'data-prob="{prob}" '
                f'data-triggers="{triggers}" '
                f'title="Kalimat #{idx} | Skor Hoaks: {prob}% | Kata Pemicu: {triggers}">'
                f'{escaped_text} '
                f'</span>'
            )
            html_parts.append(span)

        return "".join(html_parts)

