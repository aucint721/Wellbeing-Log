#!/usr/bin/env python3
"""
Command-line interface for AI Presentation Generator (Enhanced Designer)
"""

import argparse
import sys
from presentation_generator import PresentationGenerator


def main():
    # Load models/themes/animations from config so CLI stays in sync with Web UI
    preview = PresentationGenerator()
    model_choices = list(preview.list_models().keys())
    theme_choices = list(preview.list_themes().keys())
    anim = preview.config.get("animations", {})
    transition_choices = list(anim.get("slide_transitions", {"fade": "Fade", "none": "None"}).keys())
    bullet_choices = list(anim.get("bullet_animations", {"appear": "Appear", "none": "None"}).keys())
    defaults = preview.config.get("presentation", {})
    default_model = defaults.get("default_model", "claude")
    if default_model not in model_choices and model_choices:
        default_model = model_choices[0]

    parser = argparse.ArgumentParser(
        description="Generate designer presentations from text using Claude or local AI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py lesson_plan.txt -m claude -t photo_sunset --transition push --bullet-anim fly_left
  python cli.py content.txt -m hermes_auditor -t neon_cyber -n 10
  python cli.py notes.txt -m dolphin_hennie -t mint_fresh
  python cli.py --list-themes
""",
    )

    parser.add_argument("input_file", nargs="?", help="Input text file (lesson plan, notes, etc.)")
    parser.add_argument("-m", "--model", choices=model_choices, default=default_model)
    parser.add_argument("-n", "--num-slides", type=int, default=10)
    parser.add_argument(
        "-t",
        "--theme",
        choices=theme_choices,
        default=defaults.get("default_theme", "sunset_gradient"),
    )
    parser.add_argument("-o", "--output", default="presentation.pptx")
    parser.add_argument(
        "--transition",
        choices=transition_choices,
        default=defaults.get("default_slide_transition", "fade"),
        help="Slide transition style",
    )
    parser.add_argument(
        "--bullet-anim",
        choices=bullet_choices,
        default=defaults.get("default_bullet_animation", "appear"),
        help="Bullet/text line animation",
    )
    parser.add_argument("--list-models", action="store_true")
    parser.add_argument("--list-themes", action="store_true")

    args = parser.parse_args()

    try:
        generator = preview

        if args.list_models:
            print("\nAvailable AI Models\n")
            for key, model in generator.list_models().items():
                print(f"  {key}: {model['name']} ({model.get('provider', 'ollama')})")
            return 0

        if args.list_themes:
            print("\nAvailable Themes\n")
            for key, theme in generator.list_themes().items():
                kind = "photo" if theme.get("style") == "photo" else "designer"
                print(f"  {key}: {theme['name']} [{kind}]")
            return 0

        if not args.input_file:
            parser.error("input_file is required unless using --list-models or --list-themes")

        with open(args.input_file, "r", encoding="utf-8") as f:
            content = f.read()
        if not content.strip():
            print("Error: Input file is empty")
            return 1

        result = generator.generate_from_text(
            content=content,
            model_key=args.model,
            num_slides=args.num_slides,
            theme=args.theme,
            output_path=args.output,
            slide_transition=args.transition,
            bullet_animation=args.bullet_anim,
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
