#!/usr/bin/env python3
"""
AI Presentation Generator
Creates beautiful presentations from text using local Ollama models
"""

import json
import requests
import yaml
from typing import List, Dict, Optional
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import os


class PresentationGenerator:
    """Generate presentations using Ollama models"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.ollama_url = self.config['ollama']['base_url']
        self.models = self.config['models']
        self.themes = self.config['themes']
        
    def list_models(self) -> Dict:
        """List available models with details"""
        return self.models
    
    def generate_outline(self, content: str, model_key: str, num_slides: int = 10) -> Dict:
        """Generate presentation outline using selected model"""
        
        model_id = self.models[model_key]['model_id']
        
        prompt = f"""You are an expert presentation designer. Create a presentation outline from the following content.

Content:
{content}

Requirements:
- Create exactly {num_slides} slides
- Each slide should have a clear title
- Include 3-5 bullet points per slide (except title and conclusion)
- Keep text concise and impactful
- Use a logical flow

Return ONLY valid JSON in this exact format:
{{
  "title": "Main presentation title",
  "slides": [
    {{
      "type": "title",
      "title": "Title text",
      "subtitle": "Subtitle text"
    }},
    {{
      "type": "content",
      "title": "Slide title",
      "bullets": ["Point 1", "Point 2", "Point 3"]
    }},
    {{
      "type": "section",
      "title": "Section divider title"
    }}
  ]
}}

Slide types:
- "title": Opening slide with title and subtitle
- "content": Regular slide with bullets
- "section": Section divider with just a title
- "conclusion": Final slide

Generate the presentation outline now:"""

        print(f"Generating outline with {self.models[model_key]['name']}...")
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model_id,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['response'].strip()
                
                # Extract JSON from response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    outline = json.loads(json_text)
                    print(f"✓ Generated outline with {len(outline.get('slides', []))} slides")
                    return outline
                else:
                    raise ValueError("No valid JSON found in response")
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            print(f"Error generating outline: {e}")
            raise
    
    def create_presentation(self, outline: Dict, theme_key: str = "modern", output_path: str = "presentation.pptx"):
        """Create PowerPoint presentation from outline"""
        
        theme = self.themes[theme_key]
        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
        
        # Color scheme
        primary = RGBColor(*theme['primary_color'])
        accent = RGBColor(*theme['accent_color'])
        bg = RGBColor(*theme['background'])
        text = RGBColor(*theme['text_color'])
        
        print(f"Creating presentation with '{theme['name']}' theme...")
        
        for i, slide_data in enumerate(outline.get('slides', [])):
            slide_type = slide_data.get('type', 'content')
            
            if slide_type == 'title':
                self._create_title_slide(prs, slide_data, primary, accent, text)
            elif slide_type == 'section':
                self._create_section_slide(prs, slide_data, primary, text)
            elif slide_type == 'conclusion':
                self._create_conclusion_slide(prs, slide_data, accent, text)
            else:  # content
                self._create_content_slide(prs, slide_data, primary, accent, text)
            
            print(f"  ✓ Created slide {i+1}: {slide_data.get('title', 'Untitled')}")
        
        prs.save(output_path)
        print(f"\n✓ Presentation saved: {output_path}")
        return output_path
    
    def _create_title_slide(self, prs, data, primary_color, accent_color, text_color):
        """Create title slide"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
        
        # Background rectangle
        shapes = slide.shapes
        bg_shape = shapes.add_shape(
            1,  # Rectangle
            0, 0,
            prs.slide_width, prs.slide_height
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = primary_color
        bg_shape.line.fill.background()
        
        # Title
        title_box = shapes.add_textbox(
            Inches(1), Inches(2.5),
            Inches(8), Inches(1.5)
        )
        title_frame = title_box.text_frame
        title_frame.text = data.get('title', 'Presentation Title')
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(54)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        title_para.alignment = PP_ALIGN.CENTER
        
        # Subtitle
        if data.get('subtitle'):
            subtitle_box = shapes.add_textbox(
                Inches(1), Inches(4.2),
                Inches(8), Inches(1)
            )
            subtitle_frame = subtitle_box.text_frame
            subtitle_frame.text = data['subtitle']
            subtitle_para = subtitle_frame.paragraphs[0]
            subtitle_para.font.size = Pt(28)
            subtitle_para.font.color.rgb = RGBColor(255, 255, 255)
            subtitle_para.alignment = PP_ALIGN.CENTER
    
    def _create_section_slide(self, prs, data, primary_color, text_color):
        """Create section divider slide"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        
        # Colored background
        shapes = slide.shapes
        bg_shape = shapes.add_shape(
            1,
            0, 0,
            prs.slide_width, prs.slide_height
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = primary_color
        bg_shape.line.fill.background()
        
        # Section title
        title_box = shapes.add_textbox(
            Inches(1), Inches(3),
            Inches(8), Inches(1.5)
        )
        title_frame = title_box.text_frame
        title_frame.text = data.get('title', 'Section')
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(48)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        title_para.alignment = PP_ALIGN.CENTER
    
    def _create_conclusion_slide(self, prs, data, accent_color, text_color):
        """Create conclusion slide"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        
        shapes = slide.shapes
        bg_shape = shapes.add_shape(
            1,
            0, 0,
            prs.slide_width, prs.slide_height
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = accent_color
        bg_shape.line.fill.background()
        
        title_box = shapes.add_textbox(
            Inches(1), Inches(3),
            Inches(8), Inches(1.5)
        )
        title_frame = title_box.text_frame
        title_frame.text = data.get('title', 'Thank You')
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(48)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        title_para.alignment = PP_ALIGN.CENTER
    
    def _create_content_slide(self, prs, data, primary_color, accent_color, text_color):
        """Create content slide with bullets"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        shapes = slide.shapes
        
        # Title bar
        title_shape = shapes.add_shape(
            1,
            0, 0,
            prs.slide_width, Inches(1)
        )
        title_shape.fill.solid()
        title_shape.fill.fore_color.rgb = primary_color
        title_shape.line.fill.background()
        
        # Title text
        title_box = shapes.add_textbox(
            Inches(0.5), Inches(0.2),
            Inches(9), Inches(0.6)
        )
        title_frame = title_box.text_frame
        title_frame.text = data.get('title', 'Slide Title')
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(32)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        
        # Content bullets
        bullets = data.get('bullets', [])
        if bullets:
            content_box = shapes.add_textbox(
                Inches(1), Inches(1.5),
                Inches(8), Inches(5.5)
            )
            text_frame = content_box.text_frame
            text_frame.word_wrap = True
            
            for i, bullet in enumerate(bullets):
                if i == 0:
                    p = text_frame.paragraphs[0]
                else:
                    p = text_frame.add_paragraph()
                
                p.text = bullet
                p.level = 0
                p.font.size = Pt(20)
                p.font.color.rgb = text_color
                p.space_after = Pt(12)
    
    def generate_from_text(self, content: str, model_key: str, num_slides: int = 10, 
                          theme: str = "modern", output_path: str = "presentation.pptx") -> str:
        """Complete pipeline: text -> outline -> presentation"""
        
        print(f"\n{'='*60}")
        print(f"AI Presentation Generator")
        print(f"{'='*60}")
        print(f"Model: {self.models[model_key]['name']}")
        print(f"Theme: {self.themes[theme]['name']}")
        print(f"Slides: {num_slides}")
        print(f"{'='*60}\n")
        
        # Generate outline
        outline = self.generate_outline(content, model_key, num_slides)
        
        # Create presentation
        result_path = self.create_presentation(outline, theme, output_path)
        
        print(f"\n{'='*60}")
        print(f"✓ SUCCESS! Presentation created")
        print(f"{'='*60}\n")
        
        return result_path


if __name__ == "__main__":
    # Quick test
    generator = PresentationGenerator()
    
    print("\nAvailable Models:")
    for key, model in generator.list_models().items():
        print(f"  - {key}: {model['name']} - {model['description']}")
