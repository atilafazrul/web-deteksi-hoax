<template>
  <div class="flex flex-col min-h-screen bg-slate-50/60 text-slate-800">
    <!-- TOP NAVIGATION BAR -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-40">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        <!-- BRAND LOGO -->
        <div class="flex items-center space-x-3 cursor-pointer" @click="activeMainTab = 'scanner'">
          <div class="w-9 h-9 rounded-lg bg-slate-900 text-white flex items-center justify-center shadow-sm">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
            </svg>
          </div>
          <div>
            <div class="flex items-center space-x-1.5">
              <span class="text-base font-bold tracking-tight text-slate-900">CekFakta</span>
              <span class="text-[11px] font-medium text-slate-500 uppercase tracking-widest">ID</span>
            </div>
            <p class="text-[11px] text-slate-500 leading-none">Verifikasi & Deteksi Berita</p>
          </div>
        </div>

        <!-- NAVIGATION TABS -->
        <nav class="flex items-center space-x-1 text-xs font-medium">
          <button @click="activeMainTab = 'scanner'" 
            :class="activeMainTab === 'scanner' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
            class="px-3.5 py-2 rounded-lg transition-colors flex items-center space-x-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            <span>Verifikasi Berita</span>
          </button>
          
          <button @click="switchTabToHistory" 
            :class="activeMainTab === 'history' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
            class="px-3.5 py-2 rounded-lg transition-colors flex items-center space-x-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span>Riwayat</span>
            <span v-if="historyList.length > 0" class="ml-1 px-1.5 py-0.2 rounded-full text-[10px]" :class="activeMainTab === 'history' ? 'bg-slate-700 text-slate-200' : 'bg-slate-200 text-slate-700 font-semibold'">{{ historyList.length }}</span>
          </button>

          <button @click="switchTabToStats" 
            :class="activeMainTab === 'stats' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
            class="px-3.5 py-2 rounded-lg transition-colors flex items-center space-x-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
            <span>Statistik</span>
          </button>
        </nav>
      </div>
    </header>

    <!-- HERO HEADER -->
    <section v-if="activeMainTab === 'scanner'" class="border-b border-slate-200/80 bg-white pt-8 pb-7">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Verifikasi Keaslian & Deteksi Disinformasi Berita
        </h1>
        <p class="mt-2 text-sm text-slate-600 max-w-2xl mx-auto leading-relaxed">
          Masukkan tautan atau naskah berita untuk memverifikasi kredibilitas klaim, menyorot kalimat yang mencurigakan, dan menelaah kesesuaian fakta.
        </p>
      </div>
    </section>

    <!-- MAIN CONTENT -->
    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full space-y-6">

      <!-- ==================== TAB 1: SCANNER ==================== -->
      <div v-show="activeMainTab === 'scanner'" class="space-y-6">

        <!-- INPUT CARD -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          
          <!-- SEGMENTED INPUT MODE SWITCHER -->
          <div class="flex border-b border-slate-200 bg-slate-50/70 p-1">
            <button @click="inputMode = 'url'" 
              :class="inputMode === 'url' ? 'bg-white text-slate-900 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'"
              class="flex-1 py-2.5 px-4 rounded-lg text-xs sm:text-sm flex items-center justify-center space-x-2 transition">
              <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
              <span>Tautan / Link Berita (URL)</span>
            </button>
            <button @click="inputMode = 'text'" 
              :class="inputMode === 'text' ? 'bg-white text-slate-900 shadow-sm font-semibold' : 'text-slate-600 hover:text-slate-900'"
              class="flex-1 py-2.5 px-4 rounded-lg text-xs sm:text-sm flex items-center justify-center space-x-2 transition">
              <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              <span>Salin & Tempel Naskah</span>
            </button>
          </div>

          <div class="p-5 sm:p-6">
            <!-- URL FORM -->
            <div v-if="inputMode === 'url'" class="space-y-4">
              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1.5">Alamat Tautan Berita</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path></svg>
                  </div>
                  <input type="url" v-model="inputUrl" @keyup.enter="analyzeUrl" 
                    placeholder="https://turnbackhoax.id/articles/... atau portal media online lainnya" 
                    class="w-full pl-10 pr-4 py-2.5 bg-slate-50/60 border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-slate-900 focus:border-slate-900 transition">
                </div>
                <p class="text-xs text-slate-500 mt-1.5">Mendukung Kompas, Detik, CNN Indonesia, Tempo, Antara, Liputan6, TurnBackHoax, dan media online lainnya.</p>
              </div>

              <button @click="analyzeUrl" :disabled="isLoading" 
                class="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-400 text-white font-medium text-xs sm:text-sm rounded-lg flex items-center justify-center space-x-2 shadow-sm transition active:scale-[0.99]">
                <svg v-if="isLoading" class="w-4 h-4 animate-spin text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                <span>{{ isLoading ? 'Menganalisis Berita...' : 'Periksa Berita' }}</span>
              </button>
            </div>

            <!-- TEXT FORM -->
            <div v-if="inputMode === 'text'" class="space-y-4">
              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1.5">Judul Berita (Opsional)</label>
                <input type="text" v-model="inputTitle" placeholder="Contoh: Beredar Pesan Bantuan Tunai Melalui Aplikasi Pesan" 
                  class="w-full px-3.5 py-2 bg-slate-50/60 border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-slate-900 focus:border-slate-900 transition">
              </div>
              <div>
                <label class="block text-xs font-semibold text-slate-700 mb-1.5">Isi Teks Berita</label>
                <textarea v-model="inputText" rows="5" placeholder="Salin dan tempelkan teks artikel atau pesan berita yang ingin diverifikasi di sini..."
                  class="w-full p-3.5 bg-slate-50/60 border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-slate-900 focus:border-slate-900 transition"></textarea>
              </div>

              <button @click="analyzeText" :disabled="isLoading" 
                class="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-400 text-white font-medium text-xs sm:text-sm rounded-lg flex items-center justify-center space-x-2 shadow-sm transition active:scale-[0.99]">
                <svg v-if="isLoading" class="w-4 h-4 animate-spin text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                <span>{{ isLoading ? 'Menganalisis Teks...' : 'Periksa Naskah' }}</span>
              </button>
            </div>

            <!-- EXAMPLE PRESETS -->
            <div class="mt-5 pt-4 border-t border-slate-100">
              <span class="text-xs font-medium text-slate-500 mb-2 block">
                Contoh Kasus Cepat:
              </span>
              <div class="flex flex-wrap gap-2">
                <button @click="loadPreset('hoax_bansos')" class="text-xs px-3 py-1.5 rounded-md bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200/80 transition flex items-center font-medium">
                  <span class="w-1.5 h-1.5 rounded-full bg-rose-500 mr-1.5"></span> Klaim Bansos DANA
                </button>
                <button @click="loadPreset('hoax_kesehatan')" class="text-xs px-3 py-1.5 rounded-md bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200/80 transition flex items-center font-medium">
                  <span class="w-1.5 h-1.5 rounded-full bg-rose-500 mr-1.5"></span> Klaim Lemon Kanker
                </button>
                <button @click="loadPreset('valid_ekonomi')" class="text-xs px-3 py-1.5 rounded-md bg-emerald-50 text-emerald-800 hover:bg-emerald-100 border border-emerald-200/80 transition flex items-center font-medium">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-600 mr-1.5"></span> Rilis APBN Kemenkeu
                </button>
                <button @click="loadPreset('valid_bmkg')" class="text-xs px-3 py-1.5 rounded-md bg-emerald-50 text-emerald-800 hover:bg-emerald-100 border border-emerald-200/80 transition flex items-center font-medium">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-600 mr-1.5"></span> Peringatan Cuaca BMKG
                </button>
              </div>
            </div>

          </div>
        </div>

        <!-- NOTIFICATION / ERROR ALERT -->
        <div v-if="errorMessage" class="bg-rose-50 border border-rose-200 rounded-xl p-4 text-rose-900 flex items-start space-x-3">
          <svg class="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <div class="text-xs">
            <h4 class="font-bold">Gagal Melakukan Pemeriksaan</h4>
            <p class="mt-0.5 text-rose-700">{{ errorMessage }}</p>
          </div>
        </div>

        <!-- ================= RESULTS DISPLAY ================= -->
        <div v-if="currentResult" class="space-y-6">

          <!-- 1. VERDICT CARD -->
          <div :class="currentResult.is_hoax ? 'bg-rose-50/70 border-rose-200' : 'bg-emerald-50/70 border-emerald-200'" 
               class="rounded-xl p-6 shadow-sm border transition-all">
            <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              
              <!-- VERDICT LABEL & EXPLANATION -->
              <div class="space-y-2">
                <div class="flex items-center space-x-2">
                  <span :class="currentResult.is_hoax ? 'bg-rose-100 text-rose-800 border-rose-200' : 'bg-emerald-100 text-emerald-800 border-emerald-200'" 
                        class="px-2.5 py-1 rounded-md text-xs font-bold tracking-wide uppercase border">
                    {{ currentResult.verdict === 'HOAX' ? 'TERINDIKASI HOAKS' : 'TERVERIFIKASI FAKTUAL' }}
                  </span>
                  <span v-if="currentResult.language_label" class="px-2 py-0.5 rounded text-[11px] font-medium bg-white/80 text-slate-700 border border-slate-200">
                    {{ currentResult.language_label }}
                  </span>
                </div>
                <h2 class="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                  {{ currentResult.is_hoax ? 'Teks Ini Terindikasi Disinformasi atau Berita Bohong' : 'Teks Ini Terindikasi Berita Resmi dan Faktual' }}
                </h2>
                <p class="text-xs sm:text-sm text-slate-600 max-w-xl leading-relaxed">
                  {{ currentResult.is_hoax 
                    ? `Ditemukan ${currentResult.stats.high_risk_sentences} kalimat dengan indikasi klaim sensasional dan pola bahasa disinformasi.`
                    : 'Struktur naskah konsisten dengan penulisan jurnalistik formal dan menggunakan rujukan informasi yang wajar.' }}
                </p>
              </div>

              <!-- KEYAKINAN / CONFIDENCE GAUGE -->
              <div class="bg-white rounded-lg p-4 border border-slate-200/80 min-w-[260px] shadow-sm">
                <div class="flex justify-between items-center mb-1.5">
                  <span class="text-xs font-medium text-slate-500 uppercase tracking-wider">Tingkat Keyakinan</span>
                  <span class="text-lg font-bold text-slate-900">{{ currentResult.confidence }}%</span>
                </div>
                <div class="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden flex">
                  <div class="h-full bg-rose-500 transition-all duration-500" :style="{ width: currentResult.prob_hoax + '%' }"></div>
                  <div class="h-full bg-emerald-500 transition-all duration-500" :style="{ width: currentResult.prob_valid + '%' }"></div>
                </div>
                <div class="flex justify-between items-center text-[11px] font-medium text-slate-500 mt-2">
                  <span class="flex items-center"><span class="w-2 h-2 rounded-full bg-rose-500 mr-1.5"></span> Skor Hoaks: <strong class="ml-1 text-slate-800">{{ currentResult.prob_hoax }}%</strong></span>
                  <span class="flex items-center"><span class="w-2 h-2 rounded-full bg-emerald-500 mr-1.5"></span> Faktual: <strong class="ml-1 text-slate-800">{{ currentResult.prob_valid }}%</strong></span>
                </div>
              </div>
            </div>

            <!-- METRICS COUNTER SUMMARY -->
            <div class="mt-5 pt-4 border-t border-slate-200/60 grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
              <div class="bg-white/80 p-3 rounded-lg border border-slate-200/60">
                <span class="text-[11px] text-slate-500 font-medium">Total Kalimat</span>
                <p class="text-base font-bold text-slate-800 mt-0.5">{{ currentResult.stats.total_sentences }}</p>
              </div>
              <div class="bg-rose-100/50 p-3 rounded-lg border border-rose-200/60">
                <span class="text-[11px] text-rose-800 font-medium">Indikasi Kuat Hoaks</span>
                <p class="text-base font-bold text-rose-800 mt-0.5">{{ currentResult.stats.high_risk_sentences }}</p>
              </div>
              <div class="bg-amber-100/50 p-3 rounded-lg border border-amber-200/60">
                <span class="text-[11px] text-amber-800 font-medium">Perlu Verifikasi</span>
                <p class="text-base font-bold text-amber-800 mt-0.5">{{ currentResult.stats.medium_risk_sentences }}</p>
              </div>
              <div class="bg-emerald-100/50 p-3 rounded-lg border border-emerald-200/60">
                <span class="text-[11px] text-emerald-800 font-medium">Kalimat Faktual</span>
                <p class="text-base font-bold text-emerald-800 mt-0.5">{{ currentResult.stats.low_risk_sentences }}</p>
              </div>
            </div>

            <!-- QUICK ACTIONS -->
            <div class="mt-4 flex flex-wrap items-center justify-end gap-2 no-print">
              <button @click="copyShareSummary" class="text-xs font-medium px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition flex items-center space-x-1.5">
                <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path></svg>
                <span>{{ copyTextStatus || 'Salin Ringkasan' }}</span>
              </button>
              <button @click="printReport" class="text-xs font-medium px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition flex items-center space-x-1.5">
                <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
                <span>Cetak Dokumen</span>
              </button>
            </div>
          </div>

          <!-- 2. ARTICLE METADATA (IF URL) -->
          <div v-if="currentResult.metadata && currentResult.metadata.url" class="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
            <div class="flex items-start space-x-4">
              <img v-if="currentResult.metadata.image" :src="currentResult.metadata.image" alt="Thumbnail Berita" class="w-24 h-20 object-cover rounded-lg border border-slate-200 flex-shrink-0">
              <div class="flex-1 min-w-0">
                <div class="flex flex-wrap items-center gap-2 text-xs text-slate-500 mb-1">
                  <span class="font-semibold text-slate-700">{{ currentResult.metadata.domain || 'Sumber Online' }}</span>
                  <span>•</span>
                  <span>{{ currentResult.metadata.date || 'Tanggal tidak tertera' }}</span>
                  <span v-if="currentResult.metadata.author">•</span>
                  <span v-if="currentResult.metadata.author">{{ currentResult.metadata.author }}</span>
                </div>
                <h3 class="text-base font-bold text-slate-900 leading-snug truncate" :title="currentResult.title">{{ currentResult.title }}</h3>
                <a :href="currentResult.metadata.url" target="_blank" rel="noopener noreferrer" class="inline-flex items-center text-xs text-slate-700 hover:text-slate-900 font-medium underline mt-1.5">
                  <span>Lihat Halaman Asli</span>
                  <svg class="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                </a>
              </div>
            </div>
          </div>

          <!-- 3. INTERACTIVE READER: BAGIAN MANA YANG HOAX -->
          <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div class="p-4 sm:p-5 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/50">
              <div>
                <h3 class="text-base font-bold text-slate-900">
                  Sorotan Naskah Berita
                </h3>
                <p class="text-xs text-slate-500 mt-0.5">
                  Klik kalimat untuk melihat rincian probabilitas dan kata kunci indikatornya.
                </p>
              </div>

              <!-- FILTER PILLS -->
              <div class="flex items-center space-x-1 text-xs bg-white p-1 rounded-lg border border-slate-200 self-start sm:self-auto">
                <button @click="sentenceFilter = 'all'" 
                  :class="sentenceFilter === 'all' ? 'bg-slate-900 text-white font-medium' : 'text-slate-600 hover:bg-slate-100'" 
                  class="px-2.5 py-1 rounded transition">Semua</button>
                <button @click="sentenceFilter = 'high'" 
                  :class="sentenceFilter === 'high' ? 'bg-rose-600 text-white font-medium' : 'text-rose-700 hover:bg-rose-50'" 
                  class="px-2.5 py-1 rounded transition">Risiko Tinggi</button>
                <button @click="sentenceFilter = 'medium'" 
                  :class="sentenceFilter === 'medium' ? 'bg-amber-600 text-white font-medium' : 'text-amber-800 hover:bg-amber-50'" 
                  class="px-2.5 py-1 rounded transition">Perlu Ditinjau</button>
                <button @click="sentenceFilter = 'low'" 
                  :class="sentenceFilter === 'low' ? 'bg-slate-700 text-white font-medium' : 'text-slate-600 hover:bg-slate-100'" 
                  class="px-2.5 py-1 rounded transition">Faktual</button>
              </div>
            </div>

            <!-- ARTICLE READER BODY -->
            <div class="p-5 sm:p-7">
              <!-- COLOR GUIDE STRIP -->
              <div class="flex flex-wrap items-center gap-4 text-xs text-slate-600 mb-5 pb-3 border-b border-slate-100">
                <span class="text-slate-400 font-medium">Petunjuk Tanda:</span>
                <span class="flex items-center"><span class="w-3 h-3 rounded bg-rose-200 mr-1.5"></span> Merah: Indikasi Kuat Hoaks (>70%)</span>
                <span class="flex items-center"><span class="w-3 h-3 rounded bg-amber-200 mr-1.5"></span> Kuning: Perlu Verifikasi (45-70%)</span>
                <span class="flex items-center"><span class="w-3 h-3 rounded bg-slate-200 mr-1.5"></span> Polos: Kalimat Wajar / Faktual</span>
              </div>

              <!-- HIGHLIGHTED SENTENCES IN NEWSREADER / CLEAN SANS STYLE -->
              <div class="text-[15px] sm:text-base text-slate-800 leading-relaxed font-normal">
                <template v-for="s in currentResult.sentences" :key="s.sentence_index">
                  <span 
                    v-if="sentenceFilter === 'all' || s.risk_tier === sentenceFilter"
                    @click="selectSentence(s)"
                    :class="['sentence-item', 'tier-' + s.risk_tier, selectedSentence && selectedSentence.sentence_index === s.sentence_index ? 'active' : '']"
                    :title="'Kalimat #' + s.sentence_index + ' | Probabilitas: ' + s.prob_hoax + '%'">
                    {{ s.text }}
                  </span>
                </template>
              </div>
            </div>

            <!-- SELECTED SENTENCE INSPECTOR -->
            <div v-if="selectedSentence" class="m-5 sm:m-6 p-4 rounded-lg border bg-slate-50 border-slate-200">
              <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div class="space-y-1">
                  <span class="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                    Inspeksi Kalimat #{{ selectedSentence.sentence_index }} dari {{ currentResult.stats.total_sentences }}
                  </span>
                  <p class="text-sm font-medium text-slate-900 italic">
                    "{{ selectedSentence.text }}"
                  </p>
                </div>
                <span :class="selectedSentence.risk_tier === 'high' ? 'bg-rose-100 text-rose-800 border-rose-200' : selectedSentence.risk_tier === 'medium' ? 'bg-amber-100 text-amber-800 border-amber-200' : 'bg-slate-200 text-slate-800 border-slate-300'"
                      class="px-2.5 py-1 rounded-md text-xs font-semibold border flex-shrink-0 self-start">
                  Skor Hoaks: {{ selectedSentence.prob_hoax }}%
                </span>
              </div>

              <div class="mt-3 pt-3 border-t border-slate-200 flex flex-wrap items-center gap-2">
                <span class="text-xs font-medium text-slate-600">Kata Kunci Terdeteksi:</span>
                <div v-if="selectedSentence.top_hoax_triggers && selectedSentence.top_hoax_triggers.length > 0" class="flex flex-wrap gap-1.5">
                  <span v-for="w in selectedSentence.top_hoax_triggers" :key="w" class="px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-800 text-xs font-medium">
                    {{ w }}
                  </span>
                </div>
                <span v-else class="text-xs text-slate-400">Tidak ada pemicu ekstrem</span>
              </div>
            </div>
          </div>

          <!-- 4. KEYWORDS SIGNALS -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- HOAX WORDS -->
            <div class="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
              <div class="flex items-center space-x-2 mb-2">
                <span class="w-2 h-2 rounded-full bg-rose-500"></span>
                <h4 class="font-bold text-slate-900 text-sm">Kata Kunci Berkarakter Hoaks</h4>
              </div>
              <p class="text-xs text-slate-500 mb-3">Kata atau istilah dalam berita yang memperkuat indikasi disinformasi:</p>
              <div class="flex flex-wrap gap-1.5">
                <span v-for="item in currentResult.top_hoax_words" :key="item[0]" 
                  class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-rose-50 text-rose-800 border border-rose-200/80">
                  {{ item[0] }}
                </span>
                <span v-if="!currentResult.top_hoax_words || currentResult.top_hoax_words.length === 0" class="text-xs text-slate-400">
                  Tidak ditemukan istilah berisiko tinggi.
                </span>
              </div>
            </div>

            <!-- FACTUAL WORDS -->
            <div class="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
              <div class="flex items-center space-x-2 mb-2">
                <span class="w-2 h-2 rounded-full bg-emerald-600"></span>
                <h4 class="font-bold text-slate-900 text-sm">Kata Kunci Berkarakter Faktual</h4>
              </div>
              <p class="text-xs text-slate-500 mb-3">Kata yang mencerminkan gaya penulisan formal dan atribusi resmi:</p>
              <div class="flex flex-wrap gap-1.5">
                <span v-for="item in currentResult.top_valid_words" :key="item[0]" 
                  class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-emerald-50 text-emerald-800 border border-emerald-200/80">
                  {{ item[0] }}
                </span>
                <span v-if="!currentResult.top_valid_words || currentResult.top_valid_words.length === 0" class="text-xs text-slate-400">
                  Tidak ditemukan istilah formal yang dominan.
                </span>
              </div>
            </div>
          </div>

          <!-- 5. IN-DEPTH EDITORIAL ANALYSIS (AI FACT-CHECKING) -->
          <div class="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
              <div>
                <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Pemeriksaan Fakta Mendalam</span>
                <h3 class="text-lg font-bold text-slate-900">
                  Analisis Kontekstual & Nalar Jurnalistik
                </h3>
                <p class="text-xs text-slate-600 mt-0.5">Penelusuran kesesuaian klaim resmi lembaga, indikasi manipulasi linguistik, dan rekomendasi cek fakta.</p>
              </div>

              <button @click="runGeminiReasoning" :disabled="isGeminiLoading" 
                class="px-4 py-2 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-400 text-white font-medium text-xs rounded-lg transition flex items-center space-x-2 shadow-sm flex-shrink-0">
                <svg v-if="isGeminiLoading" class="w-3.5 h-3.5 animate-spin text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                <span>{{ isGeminiLoading ? 'Menganalisis Klaim...' : 'Jalankan Analisis Mendalam' }}</span>
              </button>
            </div>

            <!-- RENDERED EDITORIAL CONTENT -->
            <div class="mt-4">
              <div v-if="isGeminiLoading" class="py-8 text-center text-slate-500 text-xs">
                <svg class="w-6 h-6 animate-spin mx-auto text-slate-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                <p>Sedang menelaah klaim, regulasi kementerian, dan pola bahasa berita...</p>
              </div>
              <div v-else-if="geminiOutput" class="editorial-prose text-xs sm:text-sm bg-slate-50/70 p-5 rounded-lg border border-slate-200" v-html="renderedGeminiOutput">
              </div>
              <div v-else class="py-6 text-center text-slate-400 text-xs bg-slate-50/50 rounded-lg border border-dashed border-slate-200">
                <p>Klik tombol <b>"Jalankan Analisis Mendalam"</b> di atas untuk menghasilkan telaah jurnalisme investigatif secara komprehensif.</p>
              </div>
            </div>
          </div>

        </div>

      </div>

      <!-- ==================== TAB 2: RIWAYAT ==================== -->
      <div v-show="activeMainTab === 'history'" class="space-y-6">
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div class="flex items-center justify-between mb-5">
            <div>
              <h3 class="text-lg font-bold text-slate-900">
                Riwayat Pemeriksaan Berita
              </h3>
              <p class="text-xs text-slate-500 mt-0.5">Daftar artikel yang telah diperiksa dan diverifikasi melalui sistem.</p>
            </div>
            <button @click="fetchHistory" class="text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition flex items-center space-x-1.5">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
              <span>Segarkan Data</span>
            </button>
          </div>

          <!-- HISTORY TABLE -->
          <div v-if="historyList.length > 0" class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
              <thead>
                <tr class="border-b border-slate-200 bg-slate-50/80 text-slate-600 font-semibold uppercase tracking-wider">
                  <th class="py-3 px-3">No</th>
                  <th class="py-3 px-3">Hasil Vonis</th>
                  <th class="py-3 px-3">Judul Berita & Sumber</th>
                  <th class="py-3 px-3 text-center">Keyakinan</th>
                  <th class="py-3 px-3 text-center">Kalimat Hoaks</th>
                  <th class="py-3 px-3">Waktu Periksa</th>
                  <th class="py-3 px-3 text-right">Aksi</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="(item, idx) in historyList" :key="item.id" class="hover:bg-slate-50/70 transition">
                  <td class="py-3 px-3 font-medium text-slate-500">{{ idx + 1 }}</td>
                  <td class="py-3 px-3">
                    <span :class="item.verdict === 'HOAX' ? 'bg-rose-100 text-rose-800 border-rose-200' : 'bg-emerald-100 text-emerald-800 border-emerald-200'" 
                          class="px-2 py-0.5 rounded text-[11px] font-bold border">
                      {{ item.verdict }}
                    </span>
                  </td>
                  <td class="py-3 px-3 max-w-xs">
                    <p class="font-semibold text-slate-900 truncate" :title="item.title">{{ item.title }}</p>
                    <span class="text-[11px] text-slate-400">{{ item.domain || 'Naskah Langsung' }}</span>
                  </td>
                  <td class="py-3 px-3 text-center font-medium text-slate-800">{{ item.confidence }}%</td>
                  <td class="py-3 px-3 text-center">
                    <span class="font-bold text-rose-600">{{ item.high_risk_sentences }}</span>
                    <span class="text-slate-400"> / {{ item.total_sentences }}</span>
                  </td>
                  <td class="py-3 px-3 text-slate-500">{{ item.created_at }}</td>
                  <td class="py-3 px-3 text-right space-x-2">
                    <button @click="loadHistoryDetail(item.id)" class="text-slate-900 hover:text-slate-700 font-semibold hover:underline">
                      Buka Hasil
                    </button>
                    <button @click="deleteHistory(item.id)" class="text-rose-600 hover:text-rose-800 font-medium hover:underline">
                      Hapus
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else class="text-center py-12 text-slate-400 text-xs">
            <svg class="w-10 h-10 mx-auto mb-2 opacity-40 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            <p>Belum ada riwayat artikel yang disimpan.</p>
            <p class="text-[11px] mt-1 text-slate-400">Mulai periksa berita pada tab "Verifikasi Berita".</p>
          </div>
        </div>
      </div>

      <!-- ==================== TAB 3: STATISTIK ==================== -->
      <div v-show="activeMainTab === 'stats'" class="space-y-6">
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 class="text-lg font-bold text-slate-900 mb-5">
            Ringkasan Statistik Pemeriksaan
          </h3>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <div class="bg-slate-50 p-4 rounded-lg border border-slate-200">
              <span class="text-[11px] font-semibold text-slate-500 uppercase">Total Pemeriksaan</span>
              <p class="text-2xl font-bold text-slate-900 mt-1">{{ dbStats.total_scans }}</p>
            </div>
            <div class="bg-rose-50 p-4 rounded-lg border border-rose-200">
              <span class="text-[11px] font-semibold text-rose-800 uppercase">Hoaks Terdeteksi</span>
              <p class="text-2xl font-bold text-rose-800 mt-1">{{ dbStats.total_hoax }}</p>
            </div>
            <div class="bg-emerald-50 p-4 rounded-lg border border-emerald-200">
              <span class="text-[11px] font-semibold text-emerald-800 uppercase">Berita Faktual</span>
              <p class="text-2xl font-bold text-emerald-800 mt-1">{{ dbStats.total_valid }}</p>
            </div>
            <div class="bg-slate-50 p-4 rounded-lg border border-slate-200">
              <span class="text-[11px] font-semibold text-slate-700 uppercase">Rata-rata Keyakinan</span>
              <p class="text-2xl font-bold text-slate-800 mt-1">{{ dbStats.avg_confidence }}%</p>
            </div>
          </div>

          <!-- TOP DOMAINS -->
          <div>
            <h4 class="font-semibold text-xs text-slate-700 uppercase tracking-wider mb-2.5">Domain Berita yang Sering Diperiksa</h4>
            <div v-if="dbStats.top_domains && dbStats.top_domains.length > 0" class="divide-y divide-slate-100 border border-slate-200 rounded-lg overflow-hidden">
              <div v-for="d in dbStats.top_domains" :key="d.domain" class="p-3 flex items-center justify-between text-xs hover:bg-slate-50">
                <span class="font-medium text-slate-800">{{ d.domain }}</span>
                <span class="text-slate-500">{{ d.count }} kali diperiksa ({{ d.hoax_count }} hoaks)</span>
              </div>
            </div>
            <p v-else class="text-xs text-slate-400">Belum ada domain berita yang tersimpan.</p>
          </div>
        </div>
      </div>

    </main>

    <!-- FOOTER -->
    <footer class="bg-white border-t border-slate-200 py-6 mt-12 text-xs text-slate-500">
      <div class="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
        <p>CekFakta ID — Platform Pemeriksaan Fakta & Verifikasi Disinformasi Berita.</p>
        <p class="text-slate-400">Mendukung literasi informasi dan jurnalisme berintegritas.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

const API_BASE = '/api'

const activeMainTab = ref('scanner') // 'scanner' | 'history' | 'stats'
const inputMode = ref('url') // 'url' | 'text'
const inputUrl = ref('')
const inputTitle = ref('')
const inputText = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const currentResult = ref(null)
const selectedSentence = ref(null)
const sentenceFilter = ref('all') // 'all' | 'high' | 'medium' | 'low'
const presets = ref({})
const historyList = ref([])
const dbStats = ref({ total_scans: 0, total_hoax: 0, total_valid: 0, avg_confidence: 0, top_domains: [] })
const geminiOutput = ref('')
const isGeminiLoading = ref(false)
const copyTextStatus = ref('')

const renderedGeminiOutput = computed(() => {
  if (!geminiOutput.value) return ''
  try {
    return marked.parse(geminiOutput.value)
  } catch (e) {
    return geminiOutput.value
  }
})

const loadPresets = async () => {
  try {
    const res = await axios.get(`${API_BASE}/examples`)
    presets.value = res.data
  } catch (e) {
    console.error('Presets error:', e)
  }
}

const fetchHistory = async () => {
  try {
    const res = await axios.get(`${API_BASE}/history`)
    if (res.data.status === 'success') {
      historyList.value = res.data.history
    }
  } catch (e) {
    console.error('History error:', e)
  }
}

const fetchStats = async () => {
  try {
    const res = await axios.get(`${API_BASE}/stats`)
    if (res.data.status === 'success') {
      dbStats.value = res.data.stats
    }
  } catch (e) {
    console.error('Stats error:', e)
  }
}

const switchTabToHistory = () => {
  activeMainTab.value = 'history'
  fetchHistory()
}

const switchTabToStats = () => {
  activeMainTab.value = 'stats'
  fetchStats()
}

const loadPreset = (key) => {
  const p = presets.value[key]
  if (!p) return
  inputMode.value = 'text'
  inputTitle.value = p.title || ''
  inputText.value = p.text || ''
}

const analyzeUrl = async () => {
  if (!inputUrl.value.trim()) {
    errorMessage.value = 'Silakan masukkan URL tautan berita terlebih dahulu.'
    return
  }
  errorMessage.value = ''
  isLoading.value = true
  currentResult.value = null
  selectedSentence.value = null
  geminiOutput.value = ''

  try {
    const res = await axios.post(`${API_BASE}/analyze-url`, { url: inputUrl.value.trim() })
    if (res.data.status === 'success') {
      currentResult.value = res.data
      if (res.data.ai_explanation) {
        geminiOutput.value = res.data.ai_explanation
      }
      fetchHistory()
      fetchStats()
    } else {
      errorMessage.value = res.data.error_msg || 'Gagal memproses URL berita.'
    }
  } catch (e) {
    errorMessage.value = e.response?.data?.error_msg || e.message
  } finally {
    isLoading.value = false
  }
}

const analyzeText = async () => {
  if (!inputText.value.trim()) {
    errorMessage.value = 'Silakan masukkan teks berita terlebih dahulu.'
    return
  }
  errorMessage.value = ''
  isLoading.value = true
  currentResult.value = null
  selectedSentence.value = null
  geminiOutput.value = ''

  try {
    const res = await axios.post(`${API_BASE}/analyze-text`, {
      text: inputText.value.trim(),
      title: inputTitle.value.trim()
    })
    if (res.data.status === 'success') {
      currentResult.value = res.data
      if (res.data.ai_explanation) {
        geminiOutput.value = res.data.ai_explanation
      }
      fetchHistory()
      fetchStats()
    } else {
      errorMessage.value = res.data.error_msg || 'Gagal memeriksa naskah berita.'
    }
  } catch (e) {
    errorMessage.value = e.response?.data?.error_msg || e.message
  } finally {
    isLoading.value = false
  }
}

const selectSentence = (sentence) => {
  selectedSentence.value = sentence
}

const loadHistoryDetail = async (id) => {
  isLoading.value = true
  try {
    const res = await axios.get(`${API_BASE}/history/${id}`)
    if (res.data.status === 'success') {
      currentResult.value = res.data.data
      selectedSentence.value = null
      geminiOutput.value = res.data.data.ai_explanation || ''
      activeMainTab.value = 'scanner'
      window.scrollTo({ top: 350, behavior: 'smooth' })
    }
  } catch (e) {
    alert('Gagal memuat detail riwayat: ' + e.message)
  } finally {
    isLoading.value = false
  }
}

const deleteHistory = async (id) => {
  if (!confirm(`Hapus data riwayat #${id}?`)) return
  try {
    await axios.delete(`${API_BASE}/history/${id}`)
    fetchHistory()
    fetchStats()
    if (currentResult.value && currentResult.value.db_id === id) {
      currentResult.value = null
    }
  } catch (e) {
    alert('Gagal menghapus: ' + e.message)
  }
}

const runGeminiReasoning = async () => {
  if (!currentResult.value) return
  isGeminiLoading.value = true
  geminiOutput.value = ''

  try {
    const fullText = currentResult.value.sentences.map(s => s.text).join(' ')
    const res = await axios.post(`${API_BASE}/gemini-reasoning`, {
      text: fullText,
      label: currentResult.value.verdict,
      confidence: currentResult.value.confidence
    })
    if (res.data.status === 'success') {
      geminiOutput.value = res.data.explanation
    } else {
      geminiOutput.value = 'Gagal: ' + res.data.error_msg
    }
  } catch (e) {
    geminiOutput.value = 'Kesalahan: ' + (e.response?.data?.error_msg || e.message)
  } finally {
    isGeminiLoading.value = false
  }
}

const copyShareSummary = () => {
  if (!currentResult.value) return
  const r = currentResult.value
  const text = `[HASIL VERIFIKASI CEKFAKTA ID]\nJudul: ${r.title}\nVonis: ${r.verdict} (Keyakinan: ${r.confidence}%)\nProbabilitas Hoaks: ${r.prob_hoax}%\nKalimat Terindikasi Hoaks: ${r.stats.high_risk_sentences} dari ${r.stats.total_sentences} kalimat.\n\nDiverifikasi melalui CekFakta ID.`
  navigator.clipboard.writeText(text).then(() => {
    copyTextStatus.value = 'Tersalin!'
    setTimeout(() => { copyTextStatus.value = '' }, 2500)
  })
}

const printReport = () => {
  window.print()
}

onMounted(() => {
  loadPresets()
  fetchHistory()
  fetchStats()
})
</script>
