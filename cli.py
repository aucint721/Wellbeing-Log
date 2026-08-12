#!/usr/bin/env python3
"""
Command-line interface for AI Presentation Generator
"""

import argparse
import sys
from presentation_generator import PresentationGenerator


def main():
    parser = argparse.ArgumentParser(
        description='Generate presentations from text using local AI models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from lesson plan file
  python cli.py lesson_plan.txt -m dolphin_70b -n 15 -t modern
  
  # Quick draft with fast model
  python cli.py content.txt -m dolphin_8b -n 10
  
  # Technical presentation with Hermes
  python cli.py lecture_notes.txt -m hermes -n 20 -t education
  
Available Models:
  dolphin_8b  - Fast generation (5-10x faster)
  dolphin_70b - Premium quality (recommended)
  hermes      - Advanced reasoning for technical content
  
Available Themes:
  modern      - Modern Professional (default)
  dark        - Dark Tech
  education   - Education Blue
  warm        - Warm Earth
"""
    )
    
    parser.add_argument('input_file', help='Input text file (lesson plan, notes, etc.)')
    parser.add_argument('-m', '--model', 
                       choices=['dolphin_8b', 'dolphin_70b', 'hermes'],
                       default='dolphin_70b',
                       help='AI model to use (default: dolphin_70b)')
    parser.add_argument('-n', '--num-slides', 
                       type=int, 
                       default=10,
                       help='Number of slides to generate (default: 10)')
    parser.add_argument('-t', '--theme',
                       choices=['modern', 'dark', 'education', 'warm'],
                       default='modern',
                       help='Presentation theme (default: modern)')
    parser.add_argument('-o', '--output',
                       default='presentation.pptx',
                       help='Output filename (default: presentation.pptx)')
    parser.add_argument('--list-models',
                       action='store_true',
                       help='List available models and exit')
    
    args = parser.parse_args()
    
    try:
        generator = PresentationGenerator()
        
        if args.list_models:
            print("\n" + "="*70)
            print("Available AI Models")
            print("="*70 + "\n")
            
            for key, model in generator.list_models().items():
                print(f"📌 {key}")
                print(f"   Name: {model['name']}")
                print(f"   Speed: {model['speed']}")
                print(f"   Quality: {model['quality']}")
                print(f"   Best for: {model['best_for']}")
                print()
            
            return 0
        
        # Read input file
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.input_file}")
            return 1
        except Exception as e:
            print(f"Error reading file: {e}")
            return 1
        
        if not content.strip():
            print("Error: Input file is empty")
            return 1
        
        # Generate presentation
        result = generator.generate_from_text(
            content=content,
            model_key=args.model,
            num_slides=args.num_slides,
            theme=args.theme,
            output_path=args.output
        )
        
        print(f"Output: {result}")
        return 0
        
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        return 130
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
