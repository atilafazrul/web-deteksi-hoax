<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use App\Models\Article;
use App\Models\ArticleSentence;
use Symfony\Component\Process\Process;

class ArticleController extends Controller
{
    /**
     * Preset examples for instant testing.
     */
    private array $presets = [
        "hoax_bansos" => [
            "title" => "Bansos Saldo DANA Rp 5 Juta dari Pemerintah",
            "url" => "",
            "text" => "Beredar pesan berantai viral di WhatsApp yang mengeklaim bahwa pemerintah melalui Kementerian Sosial membagikan bansos saldo DANA gratis sebesar Rp 5.000.000 untuk seluruh masyarakat. Penerima diwajibkan segera mengklik link pendaftaran dan membagikan pesan ini ke 5 grup lainnya sebelum kuota habis. Setelah ditelusuri, Kementerian Sosial menegaskan bahwa informasi tersebut adalah hoaks dan penipuan phising."
        ],
        "hoax_kesehatan" => [
            "title" => "Air Rebusan Lemon Panas Diklaim Bunuh Sel Kanker Seketika",
            "url" => "",
            "text" => "Viral kabar rahasia kedokteran yang sengaja ditutup-tutupi farmasi bahwa meminum air rebusan lemon panas 1000 kali lebih kuat dari kemoterapi dan dapat membunuh sel kanker seketika tanpa efek samping. Dokter spesialis onkologi dan IDI mengklarifikasi bahwa klaim tersebut tidak memiliki dasar ilmiah kedokteran."
        ],
        "valid_ekonomi" => [
            "title" => "Kemenkeu Paparkan Realisasi Pendapatan Negara dalam APBN Kita",
            "url" => "",
            "text" => "Kementerian Keuangan menyelenggarakan konferensi pers APBN Kita di Jakarta. Menteri Keuangan Sri Mulyani memaparkan realisasi pendapatan negara mencapai target tahun ini didorong oleh sektor penerimaan pajak. Pemerintah terus menjaga defisit anggaran dalam batas aman sesuai undang-undang dan mengoptimalkan belanja produktif untuk perlindungan sosial."
        ],
        "valid_bmkg" => [
            "title" => "BMKG Keluarkan Peringatan Dini Cuaca Ekstrem Sepekan ke Depan",
            "url" => "",
            "text" => "Badan Meteorologi Klimatologi dan Geofisika (BMKG) merilis peringatan dini potensi cuaca ekstrem di sejumlah wilayah Indonesia sepekan ke depan. Deputi Bidang Meteorologi BMKG Guswanto mengimbau masyarakat untuk waspada terhadap potensi bencana hidrometeorologi seperti banjir dan tanah longsor. Informasi cuaca terkini dapat terus dipantau secara berkala melalui kanal resmi aplikasi Info BMKG."
        ]
    ];

    /**
     * Execute Python ML bridge using standard stdin/stdout piping.
     */
    private function runPythonBridge(array $payload): array
    {
        $projectRoot = dirname(base_path());
        $scriptPath = $projectRoot . DIRECTORY_SEPARATOR . 'run_analysis.py';

        $systemRoot = getenv('SystemRoot') ?: (getenv('SYSTEMROOT') ?: 'C:\\Windows');
        $geminiKey = env('GEMINI_API_KEY', '');
        $env = array_merge($_SERVER, $_ENV, [
            'SystemRoot' => $systemRoot,
            'SYSTEMROOT' => $systemRoot,
            'windir' => $systemRoot,
            'PATH' => getenv('PATH') ?: 'C:\\Windows\\system32;C:\\Windows',
            'PYTHONIOENCODING' => 'utf-8',
            'PYTHONUTF8' => '1',
            'GEMINI_API_KEY' => $geminiKey
        ]);

        $process = new Process(['python', $scriptPath], $projectRoot, $env);
        $process->setInput(json_encode($payload));
        $process->setTimeout(120);
        $process->run();

        if (!$process->isSuccessful()) {
            throw new \Exception('Gagal menjalankan Python ML: ' . $process->getErrorOutput());
        }

        $rawOutput = trim($process->getOutput());
        $data = json_decode($rawOutput, true);

        if (!$data) {
            throw new \Exception('Output Python tidak valid: ' . substr($rawOutput, 0, 200));
        }

        return $data;
    }

    /**
     * Save analysis result to MySQL via Eloquent.
     */
    private function saveToDatabase(array $result): int
    {
        return DB::transaction(function () use ($result) {
            $meta = $result['metadata'] ?? [];
            $stats = $result['stats'] ?? [];
            $fullText = implode(' ', array_column($result['sentences'] ?? [], 'text'));

            $article = Article::create([
                'url' => $meta['url'] ?? null,
                'domain' => $meta['domain'] ?? null,
                'site_name' => $meta['site_name'] ?? null,
                'title' => substr($result['title'] ?? 'Berita Tanpa Judul', 0, 500),
                'author' => $meta['author'] ?? 'Redaksi',
                'publish_date' => $meta['date'] ?? null,
                'image_url' => $meta['image'] ?? null,
                'full_text' => $fullText,
                'verdict' => $result['verdict'] ?? 'HOAX',
                'confidence' => $result['confidence'] ?? 0,
                'prob_hoax' => $result['prob_hoax'] ?? 0,
                'prob_valid' => $result['prob_valid'] ?? 0,
                'total_sentences' => $stats['total_sentences'] ?? 0,
                'high_risk_sentences' => $stats['high_risk_sentences'] ?? 0,
                'medium_risk_sentences' => $stats['medium_risk_sentences'] ?? 0,
                'low_risk_sentences' => $stats['low_risk_sentences'] ?? 0,
                'top_hoax_words' => $result['top_hoax_words'] ?? [],
                'top_valid_words' => $result['top_valid_words'] ?? [],
                'ai_explanation' => $result['ai_explanation'] ?? null
            ]);

            $sentencesData = [];
            foreach ($result['sentences'] ?? [] as $s) {
                $sentencesData[] = [
                    'article_id' => $article->id,
                    'sentence_index' => $s['sentence_index'] ?? 1,
                    'sentence_text' => $s['text'] ?? '',
                    'prob_hoax' => $s['prob_hoax'] ?? 0,
                    'prob_valid' => $s['prob_valid'] ?? 0,
                    'risk_tier' => $s['risk_tier'] ?? 'low',
                    'trigger_words' => json_encode($s['top_hoax_triggers'] ?? []),
                    'created_at' => now(),
                    'updated_at' => now()
                ];
            }

            if (!empty($sentencesData)) {
                ArticleSentence::insert($sentencesData);
            }

            return $article->id;
        });
    }

    public function analyzeUrl(Request $request)
    {
        $request->validate(['url' => 'required|string']);
        $url = trim($request->input('url'));

        try {
            $result = $this->runPythonBridge([
                'mode' => 'url', 
                'url' => $url,
                'api_key' => env('GEMINI_API_KEY', '')
            ]);

            if (($result['status'] ?? '') === 'success') {
                $dbId = $this->saveToDatabase($result);
                $result['db_id'] = $dbId;
            }

            return response()->json($result);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'error_msg' => $e->getMessage()
            ], 500);
        }
    }

    public function analyzeText(Request $request)
    {
        $request->validate(['text' => 'required|string']);
        $text = trim($request->input('text'));
        $title = trim($request->input('title', ''));

        try {
            $result = $this->runPythonBridge([
                'mode' => 'text',
                'text' => $text,
                'title' => $title,
                'api_key' => env('GEMINI_API_KEY', '')
            ]);

            if (($result['status'] ?? '') === 'success') {
                $dbId = $this->saveToDatabase($result);
                $result['db_id'] = $dbId;
            }

            return response()->json($result);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'error_msg' => $e->getMessage()
            ], 500);
        }
    }

    public function getHistory()
    {
        $history = Article::orderBy('id', 'desc')->take(50)->get();
        return response()->json([
            'status' => 'success',
            'history' => $history
        ]);
    }

    public function getHistoryDetail($id)
    {
        $article = Article::with('sentences')->find($id);

        if (!$article) {
            return response()->json(['status' => 'error', 'error_msg' => 'Artikel tidak ditemukan.'], 404);
        }

        // Format sentences
        $sentences = $article->sentences->map(function ($s) {
            return [
                'sentence_index' => $s->sentence_index,
                'text' => $s->sentence_text,
                'prob_hoax' => $s->prob_hoax,
                'prob_valid' => $s->prob_valid,
                'risk_tier' => $s->risk_tier,
                'risk_label' => $s->risk_tier === 'high' ? 'Tinggi (Indikasi Kuat Hoaks)' : ($s->risk_tier === 'medium' ? 'Mencurigakan' : 'Aman / Faktual'),
                'top_hoax_triggers' => is_array($s->trigger_words) ? $s->trigger_words : []
            ];
        });

        return response()->json([
            'status' => 'success',
            'data' => [
                'id' => $article->id,
                'title' => $article->title,
                'verdict' => $article->verdict,
                'is_hoax' => $article->verdict === 'HOAX',
                'confidence' => $article->confidence,
                'prob_hoax' => $article->prob_hoax,
                'prob_valid' => $article->prob_valid,
                'db_id' => $article->id,
                'stats' => [
                    'total_sentences' => $article->total_sentences,
                    'high_risk_sentences' => $article->high_risk_sentences,
                    'medium_risk_sentences' => $article->medium_risk_sentences,
                    'low_risk_sentences' => $article->low_risk_sentences
                ],
                'top_hoax_words' => $article->top_hoax_words ?? [],
                'top_valid_words' => $article->top_valid_words ?? [],
                'sentences' => $sentences,
                'metadata' => [
                    'url' => $article->url,
                    'domain' => $article->domain,
                    'date' => $article->publish_date,
                    'author' => $article->author,
                    'image' => $article->image_url
                ]
            ]
        ]);
    }

    public function deleteHistory($id)
    {
        $deleted = Article::destroy($id);
        return response()->json([
            'status' => 'success',
            'deleted' => $deleted > 0
        ]);
    }

    public function getStats()
    {
        $totalScans = Article::count();
        $totalHoax = Article::where('verdict', 'HOAX')->count();
        $totalValid = Article::where('verdict', 'VALID')->count();
        $avgConfidence = Article::avg('confidence') ?? 0;

        $topDomains = Article::select('domain', DB::raw('count(*) as count'), DB::raw("sum(case when verdict = 'HOAX' then 1 else 0 end) as hoax_count"))
            ->whereNotNull('domain')
            ->where('domain', '!=', '')
            ->groupBy('domain')
            ->orderBy('count', 'desc')
            ->take(5)
            ->get();

        return response()->json([
            'status' => 'success',
            'stats' => [
                'total_scans' => $totalScans,
                'total_hoax' => $totalHoax,
                'total_valid' => $totalValid,
                'avg_confidence' => round($avgConfidence, 1),
                'top_domains' => $topDomains
            ]
        ]);
    }

    public function getExamples()
    {
        return response()->json($this->presets);
    }

    public function geminiReasoning(Request $request)
    {
        $text = trim($request->input('text', ''));
        $label = $request->input('label', 'HOAX');
        $confidence = floatval($request->input('confidence', 95.0));

        try {
            $result = $this->runPythonBridge([
                'mode' => 'gemini',
                'text' => $text,
                'label' => $label,
                'confidence' => $confidence,
                'api_key' => env('GEMINI_API_KEY', '')
            ]);
            return response()->json($result);
        } catch (\Exception $e) {
            return response()->json(['status' => 'error', 'error_msg' => $e->getMessage()], 500);
        }
    }
}

