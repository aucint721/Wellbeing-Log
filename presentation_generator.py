#!/usr/bin/env python3
"""
AI Presentation Generator
Creates beautiful presentations from text using local Ollama models or Claude API.
Polished designer layouts: concise bullets, tight spacing, sequential appear animations.
"""

import json
import os
import requests
import yaml
from typing import Dict, List, Optional

from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# PowerPoint DrawingML / PresentationML namespaces
_NSMAP = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}
_P = "{%s}" % _NSMAP["p"]


class PresentationGenerator:
    """Generate presentations using Ollama models or Claude API with polished designer layouts."""

    MAX_BULLETS = 4
    MAX_BULLET_CHARS = 80
    MAX_BULLET_WORDS = 12

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
        """Build the polished concise content-generation prompt."""
        return f"""You are an expert presentation designer creating a captivating presentation from the following content.

Content:
{content}

CRITICAL CONTENT RULES:
- Each content slide must have EXACTLY 3-4 bullet points (NO MORE)
- Each bullet must be SHORT — maximum 8-10 words, one line on screen
- Make every word count — punchy, memorable, active verbs
- Include specific numbers or examples when possible

BAD (too long):
"Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed"

GOOD (concise):
"Computers learn from data without explicit programming"
"Performance improves automatically with more examples"
"Powers Netflix recommendations and spam filters"

TARGET AUDIENCE: Year 1 students (or general audience)
- Simple, clear language
- Visual and memorable
- Fun and engaging, not dry

Create exactly {num_slides} slides with this structure:
1. Title slide (short catchy title + brief subtitle)
2. Content slides (exactly 3-4 short bullets)
3. Section breaks (1-2 for major transitions)
4. Conclusion slide

Return ONLY valid JSON in this exact format:
{{
  "title": "Short, Catchy Title (4-6 words max)",
  "slides": [
    {{
      "type": "title",
      "title": "Short Title (4-6 words)",
      "subtitle": "Brief subtitle (8-10 words max)"
    }},
    {{
      "type": "content",
      "title": "Clear Slide Title (3-5 words)",
      "bullets": [
        "First short point (8-10 words max)",
        "Second concise insight (8-10 words max)",
        "Third memorable fact (8-10 words max)"
      ]
    }},
    {{
      "type": "section",
      "title": "Section Name (2-4 words)"
    }},
    {{
      "type": "conclusion",
      "title": "Thank You"
    }}
  ]
}}

IMPORTANT:
- Keep ALL text SHORT
- 3-4 bullets per content slide (NO MORE)
- Each bullet: ONE LINE only (8-10 words)
- Be specific and memorable
- Base the presentation on the provided content

Generate the presentation outline now:"""

    def _normalize_outline(self, outline: Dict) -> Dict:
        """Enforce concise bullets so slides never overflow."""
        for slide in outline.get("slides", []):
            if slide.get("type") != "content":
                continue
            bullets = slide.get("bullets") or []
            trimmed = []
            for bullet in bullets[: self.MAX_BULLETS]:
                text = " ".join(str(bullet).split())
                words = text.split()
                if len(words) > self.MAX_BULLET_WORDS:
                    text = " ".join(words[: self.MAX_BULLET_WORDS])
                if len(text) > self.MAX_BULLET_CHARS:
                    text = text[: self.MAX_BULLET_CHARS].rstrip() + "…"
                if text:
                    trimmed.append(text)
            slide["bullets"] = trimmed
        return outline

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
        return self._normalize_outline(outline)

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

        print(f"Creating polished presentation with '{theme['name']}' theme...")

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

    def _add_appear_animations(self, slide, shapes: List):
        """Add sequential on-click Appear animations for the given shapes."""
        if not shapes:
            return
        try:
            sld = slide._element
            # Remove any existing timing so we own the sequence
            for existing in sld.findall(f"{_P}timing"):
                sld.remove(existing)

            timing = etree.SubElement(sld, f"{_P}timing")
            tn_lst = etree.SubElement(timing, f"{_P}tnLst")
            par = etree.SubElement(tn_lst, f"{_P}par")
            c_tn = etree.SubElement(
                par,
                f"{_P}cTn",
                id="1",
                dur="indefinite",
                restart="never",
                nodeType="tmRoot",
            )
            child_tn_lst = etree.SubElement(c_tn, f"{_P}childTnLst")
            seq = etree.SubElement(child_tn_lst, f"{_P}seq", concurrent="1", nextAc="seek")
            seq_c_tn = etree.SubElement(
                seq,
                f"{_P}cTn",
                id="2",
                dur="indefinite",
                nodeType="mainSeq",
            )
            seq_children = etree.SubElement(seq_c_tn, f"{_P}childTnLst")

            next_id = 3
            for index, shape in enumerate(shapes):
                shape_id = str(shape._element.get("id") or shape.shape_id)
                delay = str(index * 250)

                par2 = etree.SubElement(seq_children, f"{_P}par")
                c_tn2 = etree.SubElement(
                    par2,
                    f"{_P}cTn",
                    id=str(next_id),
                    fill="hold",
                )
                next_id += 1
                st_cond = etree.SubElement(c_tn2, f"{_P}stCondLst")
                etree.SubElement(st_cond, f"{_P}cond", delay=delay if index == 0 else "0")
                if index > 0:
                    # After previous click/animation — use on-click for each bullet
                    pass
                # On-click trigger for each bullet after the first
                if index > 0:
                    st_cond.clear()
                    etree.SubElement(st_cond, f"{_P}cond", delay="0", evt="onClick")

                child2 = etree.SubElement(c_tn2, f"{_P}childTnLst")
                par3 = etree.SubElement(child2, f"{_P}par")
                c_tn3 = etree.SubElement(
                    par3,
                    f"{_P}cTn",
                    id=str(next_id),
                    fill="hold",
                )
                next_id += 1
                st_cond3 = etree.SubElement(c_tn3, f"{_P}stCondLst")
                etree.SubElement(st_cond3, f"{_P}cond", delay="0")
                child3 = etree.SubElement(c_tn3, f"{_P}childTnLst")

                # Appear effect (presetID 1 = appear)
                anim_effect = etree.SubElement(
                    child3,
                    f"{_P}animEffect",
                    transition="in",
                    filter="fade",
                )
                c_bhvr = etree.SubElement(anim_effect, f"{_P}cBhvr")
                c_tn4 = etree.SubElement(
                    c_bhvr,
                    f"{_P}cTn",
                    id=str(next_id),
                    dur="500",
                )
                next_id += 1
                tgt = etree.SubElement(c_bhvr, f"{_P}tgtEl")
                etree.SubElement(tgt, f"{_P}spTgt", spid=shape_id)

            # Required prevCondLst / nextCondLst stubs for main sequence
            prev = etree.SubElement(seq, f"{_P}prevCondLst")
            etree.SubElement(prev, f"{_P}cond", evt="onPrev", delay="0")
            nxt = etree.SubElement(seq, f"{_P}nextCondLst")
            etree.SubElement(nxt, f"{_P}cond", evt="onNext", delay="0")
        except Exception:
            # Content still displays correctly without animations
            pass

    def _create_title_slide(self, prs, data, primary, accent, grad_start, grad_end):
        """Polished title slide with geometric accents and tighter title sizing."""
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

        title_box = shapes.add_textbox(Inches(1), Inches(2.3), Inches(8), Inches(1.8))
        title_frame = title_box.text_frame
        title_frame.text = data.get("title", "Presentation Title")
        title_frame.word_wrap = True
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(54)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        title_para.alignment = PP_ALIGN.CENTER
        title_para.line_spacing = 1.1

        if data.get("subtitle"):
            subtitle_box = shapes.add_textbox(Inches(1.5), Inches(4.5), Inches(7), Inches(1))
            subtitle_frame = subtitle_box.text_frame
            subtitle_frame.text = data["subtitle"]
            subtitle_frame.word_wrap = True
            subtitle_para = subtitle_frame.paragraphs[0]
            subtitle_para.font.size = Pt(24)
            subtitle_para.font.color.rgb = RGBColor(255, 255, 255)
            subtitle_para.alignment = PP_ALIGN.CENTER

        return slide

    def _create_section_slide(self, prs, data, primary, accent, grad_start, grad_end):
        """Polished section divider with geometric accents."""
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

        title_box = shapes.add_textbox(Inches(1.5), Inches(3.2), Inches(7), Inches(1.2))
        title_frame = title_box.text_frame
        title_frame.text = data.get("title", "Section")
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(52)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        title_para.alignment = PP_ALIGN.CENTER

        return slide

    def _create_conclusion_slide(self, prs, data, primary, accent):
        """Polished conclusion slide."""
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

        title_box = shapes.add_textbox(Inches(1.5), Inches(3.3), Inches(7), Inches(1))
        title_frame = title_box.text_frame
        title_frame.text = data.get("title", "Thank You")
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(56)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        title_para.alignment = PP_ALIGN.CENTER

        return slide

    def _create_content_slide(self, prs, data, primary, accent, text, bg):
        """Polished content slide: tight header, spaced bullets, appear animations."""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        shapes = slide.shapes

        header1 = shapes.add_shape(1, 0, 0, prs.slide_width, Inches(1.2))
        header1.fill.solid()
        header1.fill.fore_color.rgb = primary
        header1.line.fill.background()

        header2 = shapes.add_shape(1, 0, Inches(0.6), prs.slide_width, Inches(0.6))
        header2.fill.solid()
        header2.fill.fore_color.rgb = accent
        header2.fill.transparency = 0.7
        header2.line.fill.background()

        side_bar = shapes.add_shape(1, 0, Inches(1.2), Inches(0.2), Inches(6.3))
        side_bar.fill.solid()
        side_bar.fill.fore_color.rgb = accent
        side_bar.fill.transparency = 0.3
        side_bar.line.fill.background()

        for pos in [(0.35, 0.5), (0.6, 0.5)]:
            dot = shapes.add_shape(
                MSO_SHAPE.OVAL, Inches(pos[0]), Inches(pos[1]), Inches(0.12), Inches(0.12)
            )
            dot.fill.solid()
            dot.fill.fore_color.rgb = accent
            dot.line.fill.background()

        title_box = shapes.add_textbox(Inches(0.9), Inches(0.25), Inches(8.5), Inches(0.7))
        title_frame = title_box.text_frame
        title_frame.text = data.get("title", "Slide Title")
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(36)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)

        underline = shapes.add_shape(1, Inches(0.9), Inches(1.2), Inches(1.8), Inches(0.08))
        underline.fill.solid()
        underline.fill.fore_color.rgb = accent
        underline.line.fill.background()

        bullets = (data.get("bullets") or [])[: self.MAX_BULLETS]
        animated_shapes = []
        if bullets:
            start_y = 2.0
            spacing = 0.95
            for i, bullet in enumerate(bullets):
                y_pos = start_y + (i * spacing)
                bullet_box = shapes.add_textbox(
                    Inches(1.2), Inches(y_pos), Inches(7.5), Inches(0.75)
                )
                text_frame = bullet_box.text_frame
                text_frame.word_wrap = True
                p = text_frame.paragraphs[0]
                p.text = "• " + bullet
                p.font.size = Pt(20)
                p.font.color.rgb = text
                p.line_spacing = 1.2
                animated_shapes.append(bullet_box)

        corner = shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9), Inches(6.9), Inches(0.7), Inches(0.4)
        )
        corner.fill.solid()
        corner.fill.fore_color.rgb = accent
        corner.fill.transparency = 0.7
        corner.line.fill.background()

        self._add_appear_animations(slide, animated_shapes)
        return slide

    def generate_from_text(
        self,
        content: str,
        model_key: str,
        num_slides: int = 10,
        theme: str = "modern",
        output_path: str = "presentation.pptx",
    ) -> str:
        """Complete pipeline: text -> outline -> polished designer presentation."""
        print(f"\n{'=' * 60}")
        print("AI Presentation Generator (Polished Designer)")
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
