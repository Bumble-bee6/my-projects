from flask import Flask, send_from_directory, request, jsonify, send_file
from flask_cors import CORS
import os
from get_youtube_captions_combined import get_english_captions, process_captions
from summarize_transcript import summarize_text
import re
from gtts import gTTS
import tempfile
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast, MarianMTModel, MarianTokenizer

app = Flask(__name__, static_folder='frontend')
CORS(app)

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/process', methods=['POST'])
def process_video():
    try:
        data = request.json
        video_url = data.get('url')
        summary_length = data.get('length', 'standard')
        
        if not video_url:
            return jsonify({'error': 'No video URL provided'}), 400

        # Get captions
        captions_url, video_title = get_english_captions(video_url)
        if not captions_url:
            return jsonify({'error': 'No English captions found for this video'}), 404

        # Process captions
        transcript = process_captions(captions_url)
        if not transcript:
            return jsonify({'error': 'Failed to process captions'}), 500

        # Format transcript: add newline after each timestamp
        def add_newline_after_timestamp(text):
            return re.sub(r'(\[\d{2}:\d{2}:\d{2}\])', '\n', text)
        formatted_transcript = add_newline_after_timestamp(transcript)

        # Generate summary
        summary = summarize_text(formatted_transcript, summary_length)

        # Translate summary if needed
        language = data.get('language', 'english').lower()
        if language != 'english':
            try:
                # Language code mapping for Helsinki-NLP models
                helsinki_lang_map = {
                    'hindi': 'Helsinki-NLP/opus-mt-en-hi',
                    'marathi': 'Helsinki-NLP/opus-mt-en-mr',
                    'chinese': 'Helsinki-NLP/opus-mt-en-zh',
                    'arabic': 'Helsinki-NLP/opus-mt-en-ar'
                }
                
                # Language code mapping for mBART
                mbart_lang_map = {
                    'kannada': 'kn_IN',
                    'telugu': 'te_IN',
                    'tamil': 'ta_IN'
                }
                
                if language in helsinki_lang_map:
                    try:
                        # Load Helsinki-NLP model and tokenizer
                        model_name = helsinki_lang_map[language]
                        model = MarianMTModel.from_pretrained(model_name)
                        tokenizer = MarianTokenizer.from_pretrained(model_name)
                        
                        # Tokenize and translate
                        translated = model.generate(**tokenizer(summary, return_tensors="pt", padding=True))
                        summary = tokenizer.decode(translated[0], skip_special_tokens=True)
                    except Exception as e:
                        print(f"Translation error for {language}: {str(e)}")
                        summary = f"[Translation error: {str(e)}] " + summary
                elif language in mbart_lang_map:
                    try:
                        # Load mBART model and tokenizer
                        model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
                        tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
                        
                        # Set source and target language
                        tokenizer.src_lang = "en_XX"
                        tokenizer.tgt_lang = mbart_lang_map[language]
                        
                        # Tokenize and translate
                        encoded = tokenizer(summary, return_tensors="pt")
                        generated_tokens = model.generate(
                            **encoded,
                            forced_bos_token_id=tokenizer.lang_code_to_id[mbart_lang_map[language]],
                            max_length=2500
                        )
                        
                        # Decode the translation
                        summary = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
                    except Exception as e:
                        print(f"Translation error for {language}: {str(e)}")
                        summary = f"[Translation error: {str(e)}] " + summary
                else:
                    summary = f"[Translation to '{language}' not supported] " + summary
            except Exception as e:
                summary = f"[Translation error: {str(e)}] " + summary

        return jsonify({
            'title': video_title,
            'transcript': formatted_transcript,
            'summary': summary
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/speak', methods=['POST'])
def speak():
    data = request.json
    text = data.get('text')
    language = data.get('language', 'english').lower()
    # gTTS language codes
    lang_map = {
        'english': 'en',
        'hindi': 'hi',
        'marathi': 'mr',
        'chinese': 'zh-CN',
        'arabic': 'ar',
        'kannada': 'kn',
        'telugu': 'te',
        'tamil': 'ta'
    }
    tts_lang = lang_map.get(language, 'en')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    try:
        tts = gTTS(text, lang=tts_lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            fp.flush()
            return send_file(fp.name, mimetype='audio/mpeg', as_attachment=False)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)