#!/usr/bin/env python3
"""
Command-line interface for AI Presentation Generator (Enhanced Designer)
"""

import argparse
import sys
from presentation_generator import PresentationGenerator


THEME_CHOICES = [
    "modern",
    "dark",
    "education",
    "warm",
    "neon_cyber",
    "sunset_gradient",
    "ocean_deep",
    "lavender_dream",
    "forest_minimal",
    "royal_purple",
    "coral_pink",
    "midnight_blue",
    "mint_fresh",
]

MODEL_CHOICES = ["claude", "dolphin_8b", "dolphin_70b", "hermes"]


def main():
    parser = argparse.ArgumentParser(
        description="Generate designer presentations from text using Claude or local AI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Best quality with Claude API (requires ANTHROPIC_API_KEY)
  python cli.py lesson_plan.txt -m claude -n 12 -t sunset_gradient

  # Local Ollama models
  python cli.py content.txt -m dolphin_8b -n 10 -t neon_cyber
  python cli.py lecture_notes.txt -m hermes -n 20 -t education

Available Models:
  claude       - Claude Sonnet via API (recommended)
  dolphin_8b   - Fast local generation
  dolphin_70b  - Premium local quality
  hermes       - Advanced local reasoning

Available Themes:
  Classic: modern, dark, education, warm
  Designer: neon_cyber, sunset_gradient, ocean_deep, lavender_dream,
            forest_minimal, royal_purple, coral_pink, midnight_blue, mint_fresh
""",
    )

    parser.add_argument(
        "input_file",
        nargs="?",
        help="Input text file (lesson plan, notes, etc.)",
    )
    parser.add_argument(
        "-m",
        "--model",
        choices=MODEL_CHOICES,
        default="claude",
        help="AI model to use (default: claude)",
    )
    parser.add_argument(
        "-n",
        "--num-slides",
        type=int,
        default=10,
        help="Number of slides to generate (default: 10)",
    )
    parser.add_argument(
        "-t",
        "--theme",
        choices=THEME_CHOICES,
        default="sunset_gradient",
        help="Presentation theme (default: sunset_gradient)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="presentation.pptx",
        help="Output filename (default: presentation.pptx)",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models and exit",
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List available themes and exit",
    )

    args = parser.parse_args()

    try:
        generator = PresentationGenerator()

        if args.list_models:
            print("\n" + "=" * 70)
            print("Available AI Models")
            print("=" * 70 + "\n")

            for key, model in generator.list_models().items():
                provider = model.get("provider", "ollama")
                print(f"📌 {key}")
                print(f"   Name: {model['name']}")
                print(f"   Provider: {provider}")
                print(f"   Speed: {model['speed']}")
                print(f"   Quality: {model['quality']}")
                print(f"   Best for: {model['best_for']}")
                print()

            return 0

        if args.list_themes:
            print("\n" + "=" * 70)
            print("Available Themes")
            print("=" * 70 + "\n")

            for key, theme in generator.list_themes().items():
                print(f"🎨 {key}: {theme['name']}")
            print()
            return 0

        if not args.input_file:
            parser.error("input_file is required unless using --list-models or --list-themes")

        try:
            with open(args.input_file, "r", encoding="utf-8") as f:
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

        result = generator.generate_from_text(
            content=content,
            model_key=args.model,
            num_slides=args.num_slides,
            theme=args.theme,
            output_path=args.output,
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
