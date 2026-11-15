<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Article extends Model
{
    protected $fillable = [
        'url',
        'domain',
        'site_name',
        'title',
        'author',
        'publish_date',
        'image_url',
        'full_text',
        'verdict',
        'confidence',
        'prob_hoax',
        'prob_valid',
        'total_sentences',
        'high_risk_sentences',
        'medium_risk_sentences',
        'low_risk_sentences',
        'top_hoax_words',
        'top_valid_words',
        'ai_explanation'
    ];

    protected $casts = [
        'confidence' => 'float',
        'prob_hoax' => 'float',
        'prob_valid' => 'float',
        'total_sentences' => 'integer',
        'high_risk_sentences' => 'integer',
        'medium_risk_sentences' => 'integer',
        'low_risk_sentences' => 'integer',
        'top_hoax_words' => 'array',
        'top_valid_words' => 'array',
        'created_at' => 'datetime:d M Y, H:i \W\I\B',
        'updated_at' => 'datetime:d M Y, H:i \W\I\B'
    ];

    public function sentences(): HasMany
    {
        return $this->hasMany(ArticleSentence::class)->orderBy('sentence_index', 'asc');
    }
}

