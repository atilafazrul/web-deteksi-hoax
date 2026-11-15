<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class ArticleSentence extends Model
{
    protected $fillable = [
        'article_id',
        'sentence_index',
        'sentence_text',
        'prob_hoax',
        'prob_valid',
        'risk_tier',
        'trigger_words'
    ];

    protected $casts = [
        'sentence_index' => 'integer',
        'prob_hoax' => 'float',
        'prob_valid' => 'float',
        'trigger_words' => 'array',
        'created_at' => 'datetime',
        'updated_at' => 'datetime'
    ];

    public function article(): BelongsTo
    {
        return $this->belongsTo(Article::class);
    }
}

