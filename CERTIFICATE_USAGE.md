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
- Show you a preview before creating
- Create the certificate with your choices

### Create a blank template (recommended for multiple recipients)
```bash
python3 certificate_generator.py -o my_certificate.pptx
```

### Create a certificate for a specific person
```bash
python3 certificate_generator.py \
  -o sarah_certificate.pptx \
  -n "Sarah Johnson" \
  -d "August 19, 2026" \
  -s "Dr. Michael Thompson"
```

### Customize the text
```bash
python3 certificate_generator.py \
  -o my_certificate.pptx \
  -t "Certificate of Excellence" \
  -b "For exceptional dedication and support in the classroom" \
  -n "Emily Rodriguez" \
  -d "June 2026" \
  -s "Jane Smith" \
  --signature-title "Principal"
```

### Avoid duplicate titles
If your signature already includes the title (e.g., "Principal Jane Smith"), set signature title to empty:
```bash
python3 certificate_generator.py \
  -o my_certificate.pptx \
  -s "Principal Jane Smith" \
  --signature-title ""
```

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
| `-s, --signature` | Signature line name | `[Principal/Administrator Name]` |
| `--signature-title` | Title below signature | `Principal` |
| `--theme` | Theme name | `royal_purple` |
| `--list-themes` | List all available themes | - |

## Adding Your School Logo

1. **Open the certificate** in PowerPoint, Google Slides, or LibreOffice Impress
2. **Click on the dashed box** that says "INSERT SCHOOL LOGO HERE"
3. **Delete the placeholder box**
4. **Insert your logo**: 
   - PowerPoint: Insert → Pictures → This Device
   - Google Slides: Insert → Image → Upload from computer
5. **Position and resize** your logo to fit nicely at the top

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
