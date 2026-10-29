from rest_framework import serializers
from .models import BrandProfile, GenerationThread, GeneratedImage


class BrandProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandProfile
        fields = [
            "id",
            "app_name",
            "style_prompt",
            "accent_color",
            "name",
            "description",
            "primary_color",
            "secondary_color",
            "created_at",
        ]


class GeneratedImageSerializer(serializers.ModelSerializer):
    app_name = serializers.CharField(source="thread.app_name", read_only=True)
    image_type = serializers.CharField(source="thread.image_type", read_only=True)
    parent_image_id = serializers.IntegerField(read_only=True)
    dimensions = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedImage
        fields = [
            "id",
            "thread",
            "app_name",
            "image_type",
            "round_number",
            "refinement_text",
            "template_used",
            "prompt_text",
            "image_url",
            "parent_image",
            "parent_image_id",
            "is_selected",
            "width",
            "height",
            "dimensions",
            "created_at",
        ]

    def get_dimensions(self, obj):
        return f"{obj.width}x{obj.height}"


class GenerationThreadSerializer(serializers.ModelSerializer):
    images = GeneratedImageSerializer(many=True, read_only=True)

    class Meta:
        model = GenerationThread
        fields = [
            "id",
            "app_name",
            "image_type",
            "width_px",
            "height_px",
            "original_prompt",
            "created_at",
            "images",
        ]