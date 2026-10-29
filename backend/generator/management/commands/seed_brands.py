from django.core.management.base import BaseCommand
from generator.models import BrandProfile


class Command(BaseCommand):
    help = "Seed initial brand profiles for FS-7 Image Generation Platform"

    def handle(self, *args, **options):
        brands = [
            {
                "app_name": "Campus Life",
                "name": "Campus Life",
                "style_prompt": "vibrant collegiate style, energetic student life, modern university campus, sunny natural lighting, youth activities",
                "accent_color": "#3377FF",
                "primary_color": "#3377FF",
                "secondary_color": "#99BBFF",
                "description": "Student community and campus events engagement platform",
            },
            {
                "app_name": "Carelon.engage",
                "name": "Carelon.engage",
                "style_prompt": "healthcare wellness, calm empathetic aesthetic, clean bright modern environment, caring professional atmosphere, soft ambient light",
                "accent_color": "#06C270",
                "primary_color": "#06C270",
                "secondary_color": "#DDE5E9",
                "description": "Healthcare engagement and wellness communication platform",
            },
            {
                "app_name": "LifeCykul",
                "name": "LifeCykul",
                "style_prompt": "outdoor fitness, cycling adventure, athletic dynamism, high energy sports, vibrant scenic nature, golden hour lighting",
                "accent_color": "#FF5722",
                "primary_color": "#FF5722",
                "secondary_color": "#FFCC00",
                "description": "Fitness tracking, cycling community, and outdoor wellness challenges",
            },
            {
                "app_name": "Zap Creative",
                "name": "Zap Creative",
                "style_prompt": "sleek minimalist digital tech, creative design agency aesthetic, futuristic neon geometric accents, high-end studio lighting",
                "accent_color": "#6C2BD9",
                "primary_color": "#6C2BD9",
                "secondary_color": "#E3EDFF",
                "description": "Digital marketing studio and AI creative assets generator",
            },
        ]

        created_count = 0
        updated_count = 0
        for b in brands:
            obj, created = BrandProfile.objects.update_or_create(
                app_name=b["app_name"],
                defaults=b,
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded brand profiles: {created_count} created, {updated_count} updated."
            )
        )
