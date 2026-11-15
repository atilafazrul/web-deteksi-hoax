<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return response()->json([
        'app' => 'HoaxLens ID Backend API (Laravel)',
        'status' => 'running',
        'database' => 'MySQL (db_deteksi_hoax)',
        'frontend' => 'http://localhost:5173'
    ]);
});
