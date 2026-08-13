#!/usr/bin/env python3
"""
AI Presentation Generator
Creates beautiful presentations from text using local Ollama models or Claude API.
Uses designer layouts: geometric accents, gradient simulation, and modern hierarchy.
"""

import json
import os
import requests
import yaml
from typing import Dict, List, Optional

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE


class PresentationGenerator:
    """Generate presentations using Ollama models or Claude API with designer layouts."""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.ollama_url = self.config["ollama"]["base_url"]
        self.models = self.config["models"]
        self.themes = self.config["themes"]
        self.claude_config = self.config.get("claude", {})

    def list_models(self) -> Dict:
        """List available models with details."""
        return self.models

    def list_themes(self) -> Dict:
        """List available themes."""
        return self.themes

    def _build_prompt(self, content: str, num_slides: int) -> str:
        """Build the enhanced content-generation prompt."""
        return f"""You are an expert presentation designer creating a captivating presentation from the following content.

Content:
{content}

CONTENT STYLE:
- Make bullet points PUNCHY, memorable, and impactful
- Use active voice and strong verbs
- Include specific examples and numbers when relevant
- Write like you're telling an engaging story, not a boring lecture
- Each bullet should be a complete insight, not just a fragment
- Aim for "aha!" moments that make people remember the content

TARGET AUDIENCE: Year 1 students (or general audience if not education-focused)
- Keep language clear and accessible
- Use concrete examples they can visualize
- Make it fun and engaging, not dry

Create exactly {num_slides} slides with this structure:
1. Title slide (engaging title + compelling subtitle)
2. Content slides (3-4 punchy bullets each - quality over quantity)
3. Section breaks (use 1-2 for major topic transitions)
4. Conclusion slide

Return ONLY valid JSON in this exact format:
{{
  "title": "Main presentation title (make it catchy!)",
  "slides": [
    {{
      "type": "title",
      "title": "Engaging Title Text",
      "subtitle": "Compelling subtitle that makes you want to learn more"
    }},
    {{
      "type": "content",
      "title": "Clear, Action-Oriented Slide Title",
      "bullets": [
        "First impactful point with specific detail",
        "Second memorable insight that sticks",
        "Third engaging example that illustrates the concept",
        "Optional fourth point (only if needed)"
      ]
    }},
    {{
      "type": "section",
      "title": "Major Topic Transition"
    }},
    {{
      "type": "conclusion",
      "title": "Thank You"
    }}
  ]
}}

IMPORTANT:
- Each bullet should be 1-2 lines max
- Use numbers, examples, or analogies to make points memorable
- Avoid generic statements - be specific and interesting
- Create a logical narrative flow across slides
- Base the presentation on the provided content

Generate the presentation outline now:"""

    def _extract_json_outline(self, response_text: str) -> Dict:
        """Extract and parse JSON outline from model response text."""
        response_text = response_text.strip()
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1

        if json_start < 0 or json_end <= json_start:
            raise ValueError("No valid JSON found in response")

        outline = json.loads(response_text[json_start:json_end])
        if "slides" not in outline:
            raise ValueError("Outline JSON missing 'slides' key")
        return outline

    def _generate_outline_ollama(self, content: str, model_key: str, num_slides: int) -> Dict:
        """Generate outline via local Ollama."""
        model_id = self.models[model_key]["model_id"]
        prompt = self._build_prompt(content, num_slides)

        print(f"Generating outline with {self.models[model_key]['name']} (Ollama)...")

        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": model_id,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                },
            },
            timeout=300,
        )

        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text[:200]}")

        result = response.json()
        outline = self._extract_json_outline(result["response"])
        print(f"✓ Generated outline with {len(outline.get('slides', []))} slides")
        return outline

    def _generate_outline_claude(self, content: str, num_slides: int) -> Dict:
        """Generate outline via Anthropic Claude API."""
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise ImportError(
                "anthropic package required for Claude. Install with: pip install anthropic"
            ) from e

        api_key = os.getenv("ANTHROPIC_API_KEY") or self.claude_config.get("api_key")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required for Claude model"
            )

        model_id = self.claude_config.get("model_id", "claude-sonnet-5")
        prompt = self._build_prompt(content, num_slides)

        print(f"Generating outline with Claude ({model_id})...")

        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model_id,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )

        # Claude Sonnet 5 may return thinking blocks — extract text only
        response_text = ""
        for block in message.content:
            if hasattr(block, "text"):
                response_text += block.text

        outline = self._extract_json_outline(response_text)
        print(f"✓ Generated outline with {len(outline.get('slides', []))} slides")
        return outline

    def generate_outline(self, content: str, model_key: str, num_slides: int = 10) -> Dict:
        """Generate presentation outline using the selected model."""
        if model_key not in self.models:
            raise ValueError(f"Unknown model: {model_key}. Available: {list(self.models)}")

        provider = self.models[model_key].get("provider", "ollama")
        if provider == "claude":
            return self._generate_outline_claude(content, num_slides)
        return self._generate_outline_ollama(content, model_key, num_slides)

    def create_presentation(
        self,
        outline: Dict,
        theme_key: str = "modern",
        output_path: str = "presentation.pptx",
    ) -> str:
        """Create a designer-style PowerPoint presentation from an outline."""
        if theme_key not in self.themes:
            raise ValueError(f"Unknown theme: {theme_key}. Available: {list(self.themes)}")

        theme = self.themes[theme_key]
        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)

        primary = RGBColor(*theme["primary_color"])
        accent = RGBColor(*theme["accent_color"])
        bg = RGBColor(*theme["background"])
        text = RGBColor(*theme["text_color"])

        if "gradient_colors" in theme:
            grad_start = RGBColor(*theme["gradient_colors"][0])
            grad_end = RGBColor(*theme["gradient_colors"][1])
        else:
            grad_start = primary
            grad_end = accent

        print(f"Creating presentation with '{theme['name']}' designer theme...")

        for i, slide_data in enumerate(outline.get("slides", [])):
            slide_type = slide_data.get("type", "content")

            if slide_type == "title":
                slide = self._create_title_slide(
                    prs, slide_data, primary, accent, grad_start, grad_end
                )
            elif slide_type == "section":
                slide = self._create_section_slide(
                    prs, slide_data, primary, accent, grad_start, grad_end
                )
            elif slide_type == "conclusion":
                slide = self._create_conclusion_slide(prs, slide_data, primary, accent)
            else:
                slide = self._create_content_slide(prs, slide_data, primary, accent, text, bg)

            self._add_transition(slide)
            print(f"  ✓ Created slide {i + 1}: {slide_data.get('title', 'Untitled')}")

        prs.save(output_path)
        print(f"\n✓ Presentation saved: {output_path}")
        return output_path

    def _add_transition(self, slide):
        """Best-effort fade transition (supported by some pptx builds)."""
        try:
            slide.slide.transition.type = 1  # Fade
        except Exception:
            pass

    def _create_title_slide(self, prs, data, primary, accent, grad_start, grad_end):
        """Designer title slide with geometric accents."""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        shapes = slide.shapes

        bg_shape1 = shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
        bg_shape1.fill.solid()
        bg_shape1.fill.fore_color.rgb = grad_start
        bg_shape1.line.fill.background()

        bg_shape2 = shapes.add_shape(1, 0, Inches(3), prs.slide_width, Inches(4.5))
        bg_shape2.fill.solid()
        bg_shape2.fill.fore_color.rgb = grad_end
        bg_shape2.fill.transparency = 0.3
        bg_shape2.line.fill.background()

        circle1 = shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(8), Inches(-0.5), Inches(2.5), Inches(2.5)
        )
        circle1.fill.solid()
        circle1.fill.fore_color.rgb = accent
        circle1.fill.transparency = 0.7
        circle1.line.fill.background()

        for i, pos in enumerate([(0.3, 6.8), (0.8, 6.5), (1.3, 6.9)]):
            square = shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(pos[0]),
                Inches(pos[1]),
                Inches(0.25),
                Inches(0.25),
            )
            square.fill.solid()
            square.fill.fore_color.rgb = accent
            square.fill.transparency = 0.3 * (i + 1)
            square.line.fill.background()

        accent_bar = shapes.add_shape(1, Inches(-0.5), Inches(6.5), Inches(11), Inches(1.2))
        accent_bar.fill.solid()
        accent_bar.fill.fore_color.rgb = accent
        accent_bar.fill.transparency = 0.1
        accent_bar.line.fill.background()
        accent_bar.rotation = -3

        title_box = shapes.add_textbox(Inches(0.8), Inches(2), Inches(8.4), Inches(2.2))
        title_frame = title_box.text_frame
        title_frame.text = data.get("title", "Presentation Title")
        title_frame.word_wrap = True
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(60)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        title_para.alignment = PP_ALIGN.CENTER
        title_para.line_spacing = 1.15

        if data.get("subtitle"):
            subtitle_box = shapes.add_textbox(Inches(1.2), Inches(4.5), Inches(7.6), Inches(1.3))
            subtitle_frame = subtitle_box.text_frame
            subtitle_frame.text = data["subtitle"]
            subtitle_frame.word_wrap = True
            subtitle_para = subtitle_frame.paragraphs[0]
            subtitle_para.font.size = Pt(28)
            subtitle_para.font.color.rgb = RGBColor(255, 255, 255)
            subtitle_para.alignment = PP_ALIGN.CENTER
            subtitle_para.line_spacing = 1.3

        return slide

    def _create_section_slide(self, prs, data, primary, accent, grad_start, grad_end):
        """Designer section divider with geometric accents."""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        shapes = slide.shapes

        bg1 = shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
        bg1.fill.solid()
        bg1.fill.fore_color.rgb = grad_start
        bg1.line.fill.background()

        bg2 = shapes.add_shape(1, 0, Inches(2), prs.slide_width, Inches(5.5))
        bg2.fill.solid()
        bg2.fill.fore_color.rgb = grad_end
        bg2.fill.transparency = 0.4
        bg2.line.fill.background()

        for i, offset in enumerate([0, 0.3, 0.6]):
            bar = shapes.add_shape(
                1, Inches(-1 + offset), Inches(2.5 + i * 0.1), Inches(12), Inches(0.15)
            )
            bar.fill.solid()
            bar.fill.fore_color.rgb = accent
            bar.fill.transparency = 0.4 + (i * 0.2)
            bar.line.fill.background()
            bar.rotation = 2

        circle = shapes.add_shape(MSO_SHAPE.OVAL, Inches(7.5), Inches(5), Inches(3), Inches(3))
        circle.fill.solid()
        circle.fill.fore_color.rgb = accent
        circle.fill.transparency = 0.85
        circle.line.fill.background()

        title_box = shapes.add_textbox(Inches(1), Inches(3.2), Inches(8), Inches(1.5))
        title_frame = title_box.text_frame
        title_frame.text = data.get("title", "Section")
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(56)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        title_para.alignment = PP_ALIGN.CENTER

        return slide

    def _create_conclusion_slide(self, prs, data, primary, accent):
        """Designer conclusion slide."""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        shapes = slide.shapes

        bg = shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = accent
        bg.line.fill.background()

        for i, size in enumerate([2.5, 2, 1.5]):
            ring = shapes.add_shape(
                MSO_SHAPE.OVAL,
                Inches(3.75 + i * 0.25),
                Inches(2.5 + i * 0.25),
                Inches(size),
                Inches(size),
            )
            ring.fill.solid()
            ring.fill.fore_color.rgb = RGBColor(255, 255, 255)
            ring.fill.transparency = 0.8 + (i * 0.05)
            ring.line.fill.background()

        for pos in [(0.5, 1), (1, 6.5), (8.5, 1.5), (9, 6)]:
            sq = shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(pos[0]),
                Inches(pos[1]),
                Inches(0.3),
                Inches(0.3),
            )
            sq.fill.solid()
            sq.fill.fore_color.rgb = RGBColor(255, 255, 255)
            sq.fill.transparency = 0.6
            sq.line.fill.background()

        title_box = shapes.add_textbox(Inches(1), Inches(3.2), Inches(8), Inches(1.2))
        title_frame = title_box.text_frame
        title_frame.text = data.get("title", "Thank You")
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(60)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        title_para.alignment = PP_ALIGN.CENTER

        return slide

    def _create_content_slide(self, prs, data, primary, accent, text, bg):
        """Designer content slide with visual hierarchy."""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        shapes = slide.shapes

        header1 = shapes.add_shape(1, 0, 0, prs.slide_width, Inches(1.4))
        header1.fill.solid()
        header1.fill.fore_color.rgb = primary
        header1.line.fill.background()

        header2 = shapes.add_shape(1, 0, Inches(0.7), prs.slide_width, Inches(0.7))
        header2.fill.solid()
        header2.fill.fore_color.rgb = accent
        header2.fill.transparency = 0.7
        header2.line.fill.background()

        side_bar = shapes.add_shape(1, 0, Inches(1.4), Inches(0.25), Inches(6.1))
        side_bar.fill.solid()
        side_bar.fill.fore_color.rgb = accent
        side_bar.fill.transparency = 0.3
        side_bar.line.fill.background()

        for pos in [(0.4, 0.55), (0.7, 0.55)]:
            dot = shapes.add_shape(
                MSO_SHAPE.OVAL, Inches(pos[0]), Inches(pos[1]), Inches(0.15), Inches(0.15)
            )
            dot.fill.solid()
            dot.fill.fore_color.rgb = accent
            dot.line.fill.background()

        title_box = shapes.add_textbox(Inches(1), Inches(0.3), Inches(8.5), Inches(0.9))
        title_frame = title_box.text_frame
        title_frame.text = data.get("title", "Slide Title")
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(40)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        title_para.line_spacing = 1.1

        underline = shapes.add_shape(1, Inches(1), Inches(1.4), Inches(2), Inches(0.1))
        underline.fill.solid()
        underline.fill.fore_color.rgb = accent
        underline.line.fill.background()

        bullets = data.get("bullets", [])
        if bullets:
            content_box = shapes.add_textbox(Inches(1.4), Inches(2.2), Inches(7.8), Inches(4.8))
            text_frame = content_box.text_frame
            text_frame.word_wrap = True

            for i, bullet in enumerate(bullets):
                p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
                p.text = "• " + bullet
                p.level = 0
                p.font.size = Pt(22)
                p.font.color.rgb = text
                p.space_before = Pt(10)
                p.space_after = Pt(22)
                p.line_spacing = 1.4

        corner = shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9), Inches(6.8), Inches(0.8), Inches(0.5)
        )
        corner.fill.solid()
        corner.fill.fore_color.rgb = accent
        corner.fill.transparency = 0.7
        corner.line.fill.background()

        return slide

    def generate_from_text(
        self,
        content: str,
        model_key: str,
        num_slides: int = 10,
        theme: str = "modern",
        output_path: str = "presentation.pptx",
    ) -> str:
        """Complete pipeline: text -> outline -> designer presentation."""
        print(f"\n{'=' * 60}")
        print("AI Presentation Generator (Enhanced Designer)")
        print(f"{'=' * 60}")
        print(f"Model: {self.models[model_key]['name']}")
        print(f"Theme: {self.themes[theme]['name']}")
        print(f"Slides: {num_slides}")
        print(f"{'=' * 60}\n")

        outline = self.generate_outline(content, model_key, num_slides)
        result_path = self.create_presentation(outline, theme, output_path)

        print(f"\n{'=' * 60}")
        print("✓ SUCCESS! Presentation created")
        print(f"{'=' * 60}\n")

        return result_path


if __name__ == "__main__":
    generator = PresentationGenerator()

    print("\nAvailable Models:")
    for key, model in generator.list_models().items():
        print(f"  - {key}: {model['name']} - {model['description']}")

    print("\nAvailable Themes:")
    for key, theme in generator.list_themes().items():
        print(f"  - {key}: {theme['name']}")
