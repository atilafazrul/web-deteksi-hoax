<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('articles', function (Blueprint $table) {
            $table->id();
            $table->text('url')->nullable();
            $table->string('domain')->nullable();
            $table->string('site_name')->nullable();
            $table->string('title', 500);
            $table->string('author')->nullable();
            $table->string('publish_date')->nullable();
            $table->text('image_url')->nullable();
            $table->longText('full_text');
            $table->string('verdict', 20); // HOAX or VALID
            $table->float('confidence');
            $table->float('prob_hoax');
            $table->float('prob_valid');
            $table->integer('total_sentences');
            $table->integer('high_risk_sentences');
            $table->integer('medium_risk_sentences');
            $table->integer('low_risk_sentences');
            $table->json('top_hoax_words')->nullable();
            $table->json('top_valid_words')->nullable();
            $table->longText('ai_explanation')->nullable();
            $table->timestamps();
        });

        Schema::create('article_sentences', function (Blueprint $table) {
            $table->id();
            $table->foreignId('article_id')->constrained('articles')->onDelete('cascade');
            $table->integer('sentence_index');
            $table->text('sentence_text');
            $table->float('prob_hoax');
            $table->float('prob_valid');
            $table->string('risk_tier', 20); // high, medium, low
            $table->json('trigger_words')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('article_sentences');
        Schema::dropIfExists('articles');
    }
};

