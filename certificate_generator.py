#!/usr/bin/env python3
"""
Certificate Generator
Creates professional certificate slides with logo placeholders.
Perfect for recognizing teacher aides and other school staff.
"""

import yaml
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE


class CertificateGenerator:
    """Generate certificate slides with customizable text and logo placeholders."""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.themes = self.config["themes"]

    def create_certificate(
        self,
        output_file: str,
        recipient_name: str = "[Recipient Name]",
        title: str = "Certificate of Recognition",
        body_text: str = "In recognition of outstanding dedication and service as a Teacher Aide",
        date: str = "[Date]",
        signature_line: str = "[Principal/Administrator Name]",
        theme: str = "royal_purple"
    ):
        """
        Create a certificate presentation.
        
        Args:
            output_file: Output .pptx filename
            recipient_name: Name of the recipient (or placeholder)
            title: Certificate title
            body_text: Main recognition text
            date: Date of recognition
            signature_line: Name for signature line
            theme: Theme from config.yaml (default: royal_purple for formal certificates)
        """
        
        # Get theme colors
        if theme not in self.themes:
            theme = "royal_purple"  # Fallback to formal theme
        
        theme_config = self.themes[theme]
        primary_color = RGBColor(*theme_config["primary_color"])
        accent_color = RGBColor(*theme_config["accent_color"])
        bg_color = RGBColor(*theme_config["background"])
        text_color = RGBColor(*theme_config["text_color"])
        
        # Create presentation
        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
        
        # Add blank slide
        blank_layout = prs.slide_layouts[6]  # Blank layout
        slide = prs.slides.add_slide(blank_layout)
        
        # Background
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = bg_color
        
        # Add decorative border
        border = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0.5), Inches(0.5),
            Inches(9), Inches(6.5)
        )
        border.fill.background()
        border.line.color.rgb = primary_color
        border.line.width = Pt(8)
        
        # Inner decorative border
        inner_border = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0.75), Inches(0.75),
            Inches(8.5), Inches(6)
        )
        inner_border.fill.background()
        inner_border.line.color.rgb = accent_color
        inner_border.line.width = Pt(2)
        
        # Logo placeholder box (top center)
        logo_placeholder = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(4.25), Inches(1.0),
            Inches(1.5), Inches(1.5)
        )
        logo_placeholder.fill.solid()
        logo_placeholder.fill.fore_color.rgb = RGBColor(240, 240, 240)
        logo_placeholder.line.color.rgb = primary_color
        logo_placeholder.line.width = Pt(2)
        logo_placeholder.line.dash_style = 2  # Dashed line
        
        # Logo placeholder text
        logo_text = logo_placeholder.text_frame
        logo_text.text = "INSERT\nSCHOOL\nLOGO\nHERE"
        logo_text.paragraphs[0].alignment = PP_ALIGN.CENTER
        for paragraph in logo_text.paragraphs:
            paragraph.font.size = Pt(10)
            paragraph.font.color.rgb = RGBColor(150, 150, 150)
            paragraph.font.bold = True
        
        # Title
        title_box = slide.shapes.add_textbox(
            Inches(1.5), Inches(2.75),
            Inches(7), Inches(0.6)
        )
        title_frame = title_box.text_frame
        title_frame.text = title
        title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        title_frame.paragraphs[0].font.size = Pt(36)
        title_frame.paragraphs[0].font.bold = True
        title_frame.paragraphs[0].font.color.rgb = primary_color
        
        # Presented to
        presented_box = slide.shapes.add_textbox(
            Inches(1.5), Inches(3.4),
            Inches(7), Inches(0.3)
        )
        presented_frame = presented_box.text_frame
        presented_frame.text = "Presented to"
        presented_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        presented_frame.paragraphs[0].font.size = Pt(16)
        presented_frame.paragraphs[0].font.italic = True
        presented_frame.paragraphs[0].font.color.rgb = text_color
        
        # Recipient name
        name_box = slide.shapes.add_textbox(
            Inches(1.5), Inches(3.75),
            Inches(7), Inches(0.5)
        )
        name_frame = name_box.text_frame
        name_frame.text = recipient_name
        name_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        name_frame.paragraphs[0].font.size = Pt(32)
        name_frame.paragraphs[0].font.bold = True
        name_frame.paragraphs[0].font.color.rgb = accent_color
        
        # Body text
        body_box = slide.shapes.add_textbox(
            Inches(2), Inches(4.4),
            Inches(6), Inches(0.8)
        )
        body_frame = body_box.text_frame
        body_frame.text = body_text
        body_frame.word_wrap = True
        body_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        body_frame.paragraphs[0].font.size = Pt(16)
        body_frame.paragraphs[0].font.color.rgb = text_color
        
        # Date
        date_box = slide.shapes.add_textbox(
            Inches(1.5), Inches(5.5),
            Inches(3), Inches(0.4)
        )
        date_frame = date_box.text_frame
        date_frame.text = date
        date_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        date_frame.paragraphs[0].font.size = Pt(14)
        date_frame.paragraphs[0].font.color.rgb = text_color
        
        # Signature line
        sig_line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(5.5), Inches(5.65),
            Inches(3), Inches(0.01)
        )
        sig_line.fill.solid()
        sig_line.fill.fore_color.rgb = primary_color
        sig_line.line.fill.background()
        
        # Signature name
        sig_box = slide.shapes.add_textbox(
            Inches(5.5), Inches(5.75),
            Inches(3), Inches(0.4)
        )
        sig_frame = sig_box.text_frame
        sig_frame.text = signature_line
        sig_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        sig_frame.paragraphs[0].font.size = Pt(14)
        sig_frame.paragraphs[0].font.color.rgb = text_color
        
        # Signature title
        sig_title_box = slide.shapes.add_textbox(
            Inches(5.5), Inches(6.05),
            Inches(3), Inches(0.3)
        )
        sig_title_frame = sig_title_box.text_frame
        sig_title_frame.text = "Principal"
        sig_title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        sig_title_frame.paragraphs[0].font.size = Pt(11)
        sig_title_frame.paragraphs[0].font.italic = True
        sig_title_frame.paragraphs[0].font.color.rgb = text_color
        
        # Save
        prs.save(output_file)
        print(f"✓ Certificate created: {output_file}")
        print(f"  Theme: {theme_config['name']}")
        print(f"  Recipient: {recipient_name}")
        print(f"\nTo add your school logo:")
        print(f"  1. Open {output_file} in PowerPoint or Google Slides")
        print(f"  2. Click on the 'INSERT SCHOOL LOGO HERE' box")
        print(f"  3. Delete it and insert your school logo image")
        print(f"  4. Position and resize the logo as needed")


def main():
    """CLI interface for certificate generation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate professional certificate slides for teacher aides"
    )
    parser.add_argument(
        "-o", "--output",
        default="teacher_aide_certificate.pptx",
        help="Output PowerPoint file (default: teacher_aide_certificate.pptx)"
    )
    parser.add_argument(
        "-n", "--name",
        default="[Recipient Name]",
        help="Recipient name (leave as placeholder for template)"
    )
    parser.add_argument(
        "-t", "--title",
        default="Certificate of Recognition",
        help="Certificate title"
    )
    parser.add_argument(
        "-b", "--body",
        default="In recognition of outstanding dedication and service as a Teacher Aide",
        help="Body text"
    )
    parser.add_argument(
        "-d", "--date",
        default="[Date]",
        help="Date of recognition"
    )
    parser.add_argument(
        "-s", "--signature",
        default="[Principal/Administrator Name]",
        help="Name for signature line"
    )
    parser.add_argument(
        "--theme",
        default="royal_purple",
        help="Theme name from config.yaml (default: royal_purple)"
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List available themes"
    )
    
    args = parser.parse_args()
    
    generator = CertificateGenerator()
    
    if args.list_themes:
        print("\nAvailable Certificate Themes:")
        print("-" * 50)
        for key, theme in generator.themes.items():
            print(f"  {key:20} - {theme['name']}")
        print("\nRecommended for certificates:")
        print("  royal_purple, education, midnight_blue, forest_minimal")
        return
    
    generator.create_certificate(
        output_file=args.output,
        recipient_name=args.name,
        title=args.title,
        body_text=args.body,
        date=args.date,
        signature_line=args.signature,
        theme=args.theme
    )


if __name__ == "__main__":
    main()
