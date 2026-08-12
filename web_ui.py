#!/usr/bin/env python3
"""
Web UI for AI Presentation Generator
"""

from flask import Flask, render_template, request, send_file, jsonify
from presentation_generator import PresentationGenerator
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create outputs directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

generator = PresentationGenerator()


@app.route('/')
def index():
    """Main page"""
    models = generator.list_models()
    themes = generator.themes
    return render_template('index.html', models=models, themes=themes)


@app.route('/api/models')
def get_models():
    """Get available models"""
    return jsonify(generator.list_models())


@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate presentation"""
    try:
        data = request.json
        
        content = data.get('content', '').strip()
        model_key = data.get('model', 'dolphin_70b')
        num_slides = int(data.get('num_slides', 10))
        theme = data.get('theme', 'modern')
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        if num_slides < 5 or num_slides > 30:
            return jsonify({'error': 'Number of slides must be between 5 and 30'}), 400
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"presentation_{timestamp}_{uuid.uuid4().hex[:8]}.pptx"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Generate presentation
        result_path = generator.generate_from_text(
            content=content,
            model_key=model_key,
            num_slides=num_slides,
            theme=theme,
            output_path=output_path
        )
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/download/{filename}'
        })
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download(filename):
    """Download generated presentation"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎨 AI Presentation Generator - Web UI")
    print("="*70)
    print("\nStarting server at http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
