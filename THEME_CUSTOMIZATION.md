# 🎨 Theme Customization Guide

## How to Add Professional Themes

You can easily add unlimited custom themes by editing `config.yaml`. Here's everything you need to know:

---

## 📋 Quick Start

### Add a New Theme (2 minutes):

1. Open `config.yaml`
2. Copy an existing theme
3. Modify colors
4. Save and use immediately!

---

## 🎨 Theme Structure

Each theme has 4 colors:

```yaml
theme_name:
  name: "Display Name"
  primary_color: [R, G, B]    # Header bars, section slides
  accent_color: [R, G, B]     # Highlights, conclusion slide
  background: [R, G, B]       # Slide background
  text_color: [R, G, B]       # Main text color
```

---

## 🌈 Example: Adding a "Corporate Blue" Theme

### 1. Open `config.yaml`

### 2. Add this under `themes:`:

```yaml
themes:
  # ... existing themes ...
  
  corporate_blue:
    name: "Corporate Blue"
    primary_color: [0, 51, 102]       # Dark navy blue
    accent_color: [0, 153, 204]       # Bright blue
    background: [255, 255, 255]       # White
    text_color: [33, 33, 33]          # Dark gray
```

### 3. Use it immediately:

```bash
python cli.py content.txt -t corporate_blue
```

---

## 🎨 Professional Theme Examples

### Business Professional
```yaml
business_pro:
  name: "Business Professional"
  primary_color: [42, 54, 59]        # Charcoal
  accent_color: [0, 150, 136]        # Teal
  background: [255, 255, 255]        # White
  text_color: [33, 33, 33]           # Dark gray
```

### Tech Startup
```yaml
tech_startup:
  name: "Tech Startup"
  primary_color: [94, 53, 177]       # Purple
  accent_color: [255, 193, 7]        # Amber
  background: [250, 250, 250]        # Light gray
  text_color: [33, 33, 33]           # Dark gray
```

### Healthcare
```yaml
healthcare:
  name: "Healthcare"
  primary_color: [0, 105, 148]       # Medical blue
  accent_color: [34, 167, 133]       # Mint green
  background: [255, 255, 255]        # White
  text_color: [44, 62, 80]           # Navy text
```

### Finance
```yaml
finance:
  name: "Finance"
  primary_color: [19, 41, 61]        # Deep navy
  accent_color: [218, 165, 32]       # Gold
  background: [255, 255, 255]        # White
  text_color: [33, 33, 33]           # Dark gray
```

### Creative Agency
```yaml
creative:
  name: "Creative Agency"
  primary_color: [255, 87, 34]       # Vibrant orange
  accent_color: [156, 39, 176]       # Purple
  background: [255, 255, 255]        # White
  text_color: [33, 33, 33]           # Dark gray
```

### Academic
```yaml
academic:
  name: "Academic"
  primary_color: [139, 0, 0]         # Dark red
  accent_color: [184, 134, 11]       # Dark goldenrod
  background: [255, 255, 255]        # White
  text_color: [51, 51, 51]           # Dark gray
```

### Minimalist
```yaml
minimalist:
  name: "Minimalist"
  primary_color: [96, 96, 96]        # Gray
  accent_color: [189, 189, 189]      # Light gray
  background: [255, 255, 255]        # White
  text_color: [33, 33, 33]           # Dark gray
```

### Nature
```yaml
nature:
  name: "Nature"
  primary_color: [56, 142, 60]       # Forest green
  accent_color: [255, 167, 38]       # Orange
  background: [245, 245, 245]        # Off-white
  text_color: [51, 51, 51]           # Dark gray
```

---

## 🎨 Finding Perfect Colors

### Method 1: Use Color Picker Tools

**Coolors.co** (Free online tool):
1. Go to: https://coolors.co
2. Generate palettes or browse trending ones
3. Click colors to get RGB values
4. Copy into your theme

**Adobe Color** (Free):
1. Go to: https://color.adobe.com
2. Explore color wheels and harmonies
3. Export RGB values

### Method 2: Copy from Brand Guidelines

If you have company brand colors:
```
Brand Blue: #0033CC
Convert to RGB: (0, 51, 204)
```

Use in theme:
```yaml
primary_color: [0, 51, 204]
```

### Method 3: Use Existing Presentations

Open PowerPoint presentation you like:
1. Right-click on colored shape
2. Format Shape → Fill → More Colors
3. See RGB values
4. Copy to theme

---

## 🎯 Color Psychology for Presentations

### Professional/Business
- **Blue**: Trust, stability, professionalism
- **Gray**: Neutral, sophisticated, timeless
- **Navy**: Authority, confidence, corporate

### Creative/Marketing  
- **Purple**: Creative, innovative, unique
- **Orange**: Energetic, friendly, confident
- **Teal**: Modern, balanced, refreshing

### Education/Training
- **Blue**: Focus, learning, calm
- **Green**: Growth, natural, balanced
- **Red**: Important, urgent, memorable

### Technical/Scientific
- **Dark Blue**: Analytical, precise, technical
- **Gray**: Objective, factual, serious
- **Green**: Data, growth, positive trends

---

## 📐 Theme Design Best Practices

### 1. Contrast is Key
```yaml
# Good - High contrast
primary_color: [0, 51, 102]      # Dark blue
text_color: [255, 255, 255]      # White text

# Bad - Low contrast
primary_color: [200, 200, 200]   # Light gray
text_color: [180, 180, 180]      # Lighter gray (hard to read!)
```

### 2. Limit Your Palette
```yaml
# Good - 2-3 main colors
primary_color: [Navy]
accent_color: [Gold]
background: [White]

# Avoid - Too many competing colors
```

### 3. Consider Your Audience
```yaml
# Corporate audience
primary_color: [33, 33, 33]      # Conservative dark gray

# Creative audience
primary_color: [255, 87, 34]     # Bold orange
```

### 4. Test Readability
- Dark primary + white text = ✅ Good
- Light primary + black text = ✅ Good
- Mid-tone + any text = ❌ Poor contrast

---

## 🔧 Advanced Customization

### Want to Change Slide Layouts?

Edit `presentation_generator.py`:

**Add Logo:**
```python
def _create_title_slide(self, prs, data, primary_color, accent_color, text_color):
    # ... existing code ...
    
    # Add logo
    logo_path = "path/to/logo.png"
    left = Inches(8.5)
    top = Inches(0.5)
    logo = slide.shapes.add_picture(logo_path, left, top, height=Inches(0.8))
```

**Change Font Sizes:**
```python
title_para.font.size = Pt(54)  # Change from 54 to your preference
```

**Adjust Spacing:**
```python
p.space_after = Pt(16)  # Change bullet spacing
```

---

## 🎨 Quick Theme Generator Tool

Want a tool to preview colors? Add this to your setup:

```python
# theme_preview.py
from pptx import Presentation
from pptx.util import Inches
from pptx.dml.color import RGBColor

def preview_theme(primary, accent, bg, text, name):
    """Create a single-slide preview of a theme"""
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Show all colors
    shapes = slide.shapes
    
    # Primary color box
    box1 = shapes.add_shape(1, Inches(1), Inches(1), Inches(2), Inches(1))
    box1.fill.solid()
    box1.fill.fore_color.rgb = RGBColor(*primary)
    
    # Accent color box
    box2 = shapes.add_shape(1, Inches(4), Inches(1), Inches(2), Inches(1))
    box2.fill.solid()
    box2.fill.fore_color.rgb = RGBColor(*accent)
    
    prs.save(f"preview_{name}.pptx")
    print(f"Preview saved: preview_{name}.pptx")

# Test it
preview_theme([0, 51, 102], [0, 153, 204], [255, 255, 255], [33, 33, 33], "test")
```

---

## 📊 Theme Library

Here's a complete set of 12 professional themes ready to copy:

```yaml
themes:
  modern:
    name: "Modern Professional"
    primary_color: [68, 114, 196]
    accent_color: [237, 125, 49]
    background: [255, 255, 255]
    text_color: [0, 0, 0]
    
  dark:
    name: "Dark Tech"
    primary_color: [41, 128, 185]
    accent_color: [231, 76, 60]
    background: [44, 62, 80]
    text_color: [236, 240, 241]
    
  education:
    name: "Education Blue"
    primary_color: [52, 152, 219]
    accent_color: [46, 204, 113]
    background: [255, 255, 255]
    text_color: [44, 62, 80]
    
  warm:
    name: "Warm Earth"
    primary_color: [211, 84, 0]
    accent_color: [243, 156, 18]
    background: [255, 255, 255]
    text_color: [51, 51, 51]
    
  corporate:
    name: "Corporate Blue"
    primary_color: [0, 51, 102]
    accent_color: [0, 153, 204]
    background: [255, 255, 255]
    text_color: [33, 33, 33]
    
  creative:
    name: "Creative Agency"
    primary_color: [255, 87, 34]
    accent_color: [156, 39, 176]
    background: [255, 255, 255]
    text_color: [33, 33, 33]
    
  finance:
    name: "Finance Gold"
    primary_color: [19, 41, 61]
    accent_color: [218, 165, 32]
    background: [255, 255, 255]
    text_color: [33, 33, 33]
    
  healthcare:
    name: "Healthcare"
    primary_color: [0, 105, 148]
    accent_color: [34, 167, 133]
    background: [255, 255, 255]
    text_color: [44, 62, 80]
    
  startup:
    name: "Tech Startup"
    primary_color: [94, 53, 177]
    accent_color: [255, 193, 7]
    background: [250, 250, 250]
    text_color: [33, 33, 33]
    
  minimalist:
    name: "Minimalist Gray"
    primary_color: [96, 96, 96]
    accent_color: [189, 189, 189]
    background: [255, 255, 255]
    text_color: [33, 33, 33]
    
  nature:
    name: "Nature Green"
    primary_color: [56, 142, 60]
    accent_color: [255, 167, 38]
    background: [245, 245, 245]
    text_color: [51, 51, 51]
    
  academic:
    name: "Academic Traditional"
    primary_color: [139, 0, 0]
    accent_color: [184, 134, 11]
    background: [255, 255, 255]
    text_color: [51, 51, 51]
```

---

## 🚀 Using Your Custom Themes

### In CLI:
```bash
python cli.py content.txt -t corporate
```

### In Web UI:
Themes appear automatically in the theme selector!

### In Python:
```python
gen.generate_from_text(
    content=text,
    model_key="claude",
    theme="corporate"  # Your custom theme name
)
```

---

## ✨ Next Level: Import PowerPoint Template

Want to use an existing PowerPoint template? We can add that feature:

```python
def import_template(self, template_path):
    """Import colors from existing PowerPoint"""
    prs = Presentation(template_path)
    # Extract colors from template
    # Auto-generate theme config
```

This would let you:
1. Design slides in PowerPoint
2. Import the theme
3. Generate presentations matching your template

---

## 🎯 Summary

**Adding themes is EASY:**
1. Edit config.yaml
2. Add your colors
3. Use immediately

**You can have unlimited themes!**
- Copy the examples above
- Use online color tools
- Match your brand
- Create theme libraries

**Ready to see the quality?** Run the demo script to generate sample presentations! 🚀
