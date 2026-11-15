<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ArticleController;

Route::post('/analyze-url', [ArticleController::class, 'analyzeUrl']);
Route::post('/analyze-text', [ArticleController::class, 'analyzeText']);
Route::get('/history', [ArticleController::class, 'getHistory']);
Route::get('/history/{id}', [ArticleController::class, 'getHistoryDetail']);
Route::delete('/history/{id}', [ArticleController::class, 'deleteHistory']);
Route::get('/stats', [ArticleController::class, 'getStats']);
Route::get('/examples', [ArticleController::class, 'getExamples']);
Route::post('/gemini-reasoning', [ArticleController::class, 'geminiReasoning']);
