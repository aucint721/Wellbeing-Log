# Certificate Generator - Quick Start Guide

A simple tool to create professional certificates for teacher aides and other school staff.

## Quick Examples

### ✨ Interactive Mode (EASIEST - Recommended!)
Just run without any arguments and it will guide you through all options:
```bash
python3 certificate_generator.py
```

You can also explicitly use the `-i` flag:
```bash
python3 certificate_generator.py -i
```

This will:
- Show you all available themes organized by category
- Let you pick a theme by number or name
- Ask for recipient name, date, signature, etc.
- Ask for your school logo file path (optional - automatically inserts it!)
- Show you a preview before creating
- Create the certificate with your choices

### Create a blank template (recommended for multiple recipients)
```bash
python3 certificate_generator.py -o my_certificate.pptx
```

### Create a personalized certificate
```bash
python3 certificate_generator.py \
  -n "Sarah Johnson" \
  -d "August 19, 2026" \
  -s "Dr. Michael Thompson"
```

### Create with your school logo
```bash
python3 certificate_generator.py \
  -n "Sarah Johnson" \
  -d "August 19, 2026" \
  -s "Jane Smith" \
  --logo ~/Desktop/school_logo.png
```

### Customize the text
```bash
python3 certificate_generator.py \
  -o my_certificate.pptx \
  -t "Certificate of Excellence" \
  -b "For exceptional dedication and support in the classroom" \
  -n "Emily Rodriguez" \
  -d "June 2026" \
  -s "Jane Smith"
```

**Note:** The title "Principal" is automatically added below the signature name.

### Try different themes
```bash
# List all available themes
python3 certificate_generator.py --list-themes

# Use a specific theme
python3 certificate_generator.py -o cert.pptx --theme education
python3 certificate_generator.py -o cert.pptx --theme royal_purple
python3 certificate_generator.py -o cert.pptx --theme midnight_blue
python3 certificate_generator.py -o cert.pptx --theme forest_minimal
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output PowerPoint file | `teacher_aide_certificate.pptx` |
| `-n, --name` | Recipient name | `[Recipient Name]` |
| `-t, --title` | Certificate title | `Certificate of Recognition` |
| `-b, --body` | Body text | `In recognition of outstanding dedication...` |
| `-d, --date` | Date of recognition | `[Date]` |
| `-s, --signature` | Principal name (title "Principal" added automatically) | `[Name]` |
| `--logo` | Path to logo image file (PNG, JPG, etc.) | None (shows placeholder) |
| `--theme` | Theme name | `royal_purple` |
| `--list-themes` | List all available themes | - |

## Adding Your School Logo

### Option 1: Automatic (Recommended!)

When running the interactive mode, you'll be asked for your logo file path:
```
Path to logo file (PNG/JPG) [leave blank for placeholder]: ~/Desktop/school_logo.png
```

Just type or paste the path to your logo file, and it will be automatically inserted!

**Tips:**
- Use `~/Desktop/school_logo.png` for files on your Desktop
- Use tab-completion to help find the file path
- Drag and drop the file into Terminal to get the full path
- Supports PNG, JPG, and most image formats

### Option 2: Manual (If you prefer)

1. **Leave the logo path blank** when prompted (just press Enter)
2. **Open the certificate** in PowerPoint, Google Slides, or LibreOffice Impress
3. **Click on the dashed box** that says "INSERT SCHOOL LOGO HERE"
4. **Delete the placeholder box**
5. **Insert your logo**: 
   - PowerPoint: Insert → Pictures → This Device
   - Google Slides: Insert → Image → Upload from computer
6. **Position and resize** your logo to fit nicely at the top

## Tips

- **Use the blank template** if you need to create certificates for multiple people - just duplicate the slide and change the names in PowerPoint
- **Recommended themes for formal certificates**: royal_purple, education, midnight_blue, forest_minimal
- **For a modern look**: sunset_gradient, ocean_deep, mint_fresh
- **Save as PDF** in PowerPoint to ensure consistent formatting when printing
- **Test print** one certificate first to check colors and layout

## Batch Creation

To create multiple certificates at once, create a simple bash script:

```bash
#!/bin/bash
# create_all_certificates.sh

python3 certificate_generator.py -o certificates/sarah_johnson.pptx -n "Sarah Johnson" -d "June 2026" -s "Principal Smith"
python3 certificate_generator.py -o certificates/maria_garcia.pptx -n "Maria Garcia" -d "June 2026" -s "Principal Smith"
python3 certificate_generator.py -o certificates/john_davis.pptx -n "John Davis" -d "June 2026" -s "Principal Smith"
```

Then run: `chmod +x create_all_certificates.sh && ./create_all_certificates.sh`

## Sample Output Files

Three sample certificates have been created in `/opt/cursor/artifacts/`:
- `certificate_royal_purple.pptx` - Formal purple theme with sample name
- `certificate_education.pptx` - Blue education theme with sample name  
- `certificate_template_blank.pptx` - Blank template ready for your use

## Need Help?

Run `python3 certificate_generator.py --help` for full command reference.
