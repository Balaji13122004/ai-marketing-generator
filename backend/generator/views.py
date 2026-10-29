import logging
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BrandProfile, GenerationThread, GeneratedImage
from .serializers import (
    BrandProfileSerializer,
    GenerationThreadSerializer,
    GeneratedImageSerializer,
)
from .templates import resolve_dimensions
from .services import (
    build_effective_prompt,
    generate_round_variations,
    ImageGenerationError,
)

logger = logging.getLogger(__name__)


class BrandProfileListView(generics.ListAPIView):
    """
    GET /api/brand-profiles/
    List seeded brand profiles with style prompts and accent colors.
    """
    queryset = BrandProfile.objects.all().order_by("id")
    serializer_class = BrandProfileSerializer


class ThreadCreateView(APIView):
    """
    POST /api/threads/
    Starts a new generation thread (Round 1).
    Generates exactly 3 real variations composited with parametric templates.
    """
    def post(self, request):
        app_name = request.data.get("app_name", "").strip()
        image_type = request.data.get("image_type", "banner").strip().lower()
        prompt = request.data.get("prompt", "").strip()

        if not prompt:
            return Response(
                {"error": "Prompt is required to generate images."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not app_name:
            return Response(
                {"error": "app_name is required to apply branding."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Custom dimensions if specified
        custom_width = request.data.get("custom_width")
        custom_height = request.data.get("custom_height")
        custom_unit = request.data.get("custom_unit", "px")

        # Resolve dimensions using FS-7 rules & 96 DPI conversion
        try:
            target_w, target_h = resolve_dimensions(
                image_type=image_type,
                custom_width=custom_width,
                custom_height=custom_height,
                custom_unit=custom_unit,
            )
        except Exception as e:
            return Response(
                {"error": f"Invalid dimension specifications: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Lookup brand profile
        brand = BrandProfile.objects.filter(app_name__iexact=app_name).first()
        if not brand:
            # Fallback to create or find by name
            brand = BrandProfile.objects.filter(name__iexact=app_name).first()

        # Create GenerationThread
        thread = GenerationThread.objects.create(
            app_name=app_name,
            image_type=image_type,
            width_px=target_w,
            height_px=target_h,
            original_prompt=prompt,
            prompt=prompt,
            brand_profile=brand,
        )

        effective_prompt = build_effective_prompt(
            base_prompt=prompt,
            brand_profile=brand,
        )

        # Generate 3 variations
        try:
            generated_images = generate_round_variations(
                thread=thread,
                round_number=1,
                effective_prompt=effective_prompt,
                brand_profile=brand,
            )
        except ImageGenerationError as e:
            # Clean up empty thread on generation failure
            thread.delete()
            logger.error(f"Image generation failed: {e}")
            return Response(
                {"error": f"AI generation service failure: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception as e:
            thread.delete()
            logger.exception("Unexpected error in ThreadCreateView")
            return Response(
                {"error": f"Internal generation failure: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        results = [
            {
                "id": img.id,
                "image_url": img.image_url,
                "template_used": img.template_used,
                "is_selected": img.is_selected,
                "width": img.width,
                "height": img.height,
            }
            for img in generated_images
        ]

        return Response(
            {
                "thread_id": thread.id,
                "round_number": 1,
                "results": results,
            },
            status=status.HTTP_200_OK,
        )


class ThreadRefineView(APIView):
    """
    POST /api/threads/{id}/refine/
    Picks one image from a previous round and generates 3 new variations (Round 2+).
    """
    def post(self, request, id):
        thread = get_object_or_404(GenerationThread, id=id)

        selected_image_id = request.data.get("selected_image_id")
        refinement_instruction = request.data.get("refinement_instruction", "").strip()

        if not selected_image_id:
            return Response(
                {"error": "selected_image_id is required for refinement."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not refinement_instruction:
            return Response(
                {"error": "refinement_instruction is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        parent_img = GeneratedImage.objects.filter(id=selected_image_id, thread=thread).first()
        if not parent_img:
            return Response(
                {"error": f"Image ID {selected_image_id} does not belong to thread #{id}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark parent image as selected
        parent_img.is_selected = True
        parent_img.save(update_fields=["is_selected"])

        # Determine next round number
        latest_img = thread.images.order_by("-round_number").first()
        next_round = (latest_img.round_number + 1) if latest_img else 2

        # Accumulate prompt: Original prompt + prior refinement trail + new instruction
        brand = thread.brand_profile

        # Traverse parent lineage to collect prior refinement instructions
        refinement_chain = []
        curr = parent_img
        while curr:
            if curr.refinement_text and curr.refinement_text.strip():
                refinement_chain.insert(0, curr.refinement_text.strip())
            curr = curr.parent_image

        refinement_chain.append(refinement_instruction.strip())
        combined_refinements = " | ".join(refinement_chain)

        effective_prompt = build_effective_prompt(
            base_prompt=thread.original_prompt,
            brand_profile=brand,
            refinement_text=combined_refinements,
        )

        try:
            new_variations = generate_round_variations(
                thread=thread,
                round_number=next_round,
                effective_prompt=effective_prompt,
                brand_profile=brand,
                refinement_text=refinement_instruction,
                parent_image=parent_img,
            )
        except ImageGenerationError as e:
            logger.error(f"Refinement generation failed: {e}")
            return Response(
                {"error": f"AI generation service failure: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception as e:
            logger.exception("Unexpected error in ThreadRefineView")
            return Response(
                {"error": f"Internal refinement failure: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        results = [
            {
                "id": img.id,
                "image_url": img.image_url,
                "template_used": img.template_used,
                "is_selected": img.is_selected,
                "width": img.width,
                "height": img.height,
            }
            for img in new_variations
        ]

        return Response(
            {
                "thread_id": thread.id,
                "round_number": next_round,
                "results": results,
            },
            status=status.HTTP_200_OK,
        )


class ThreadDetailView(APIView):
    """
    GET /api/threads/{id}/
    Returns full thread history grouped round-by-round.
    """
    def get(self, request, id):
        thread = get_object_or_404(
            GenerationThread.objects.prefetch_related("images"),
            id=id,
        )

        # Group images by round_number
        images = list(thread.images.all().order_by("round_number", "id"))
        rounds_dict = {}
        for img in images:
            r_num = img.round_number
            if r_num not in rounds_dict:
                rounds_dict[r_num] = {
                    "round_number": r_num,
                    "refinement_instruction": None,
                    "images": [],
                }
            if img.refinement_text and not rounds_dict[r_num]["refinement_instruction"]:
                rounds_dict[r_num]["refinement_instruction"] = img.refinement_text
            rounds_dict[r_num]["images"].append({
                "id": img.id,
                "image_url": img.image_url,
                "template_used": img.template_used,
                "parent_image_id": img.parent_image_id,
                "is_selected": img.is_selected,
                "width": img.width,
                "height": img.height,
                "created_at": img.created_at,
            })

        rounds_list = [rounds_dict[k] for k in sorted(rounds_dict.keys())]

        return Response({
            "thread_id": thread.id,
            "app_name": thread.app_name,
            "image_type": thread.image_type,
            "width_px": thread.width_px,
            "height_px": thread.height_px,
            "original_prompt": thread.original_prompt,
            "created_at": thread.created_at,
            "rounds": rounds_list,
        })


class ImageLibraryView(generics.ListAPIView):
    """
    GET /api/images/
    Browse flat list of all generated images across all threads, newest first.
    Supports optional query parameters:
    - ?app_name=Campus Life
    - ?image_type=banner
    """
    serializer_class = GeneratedImageSerializer

    def get_queryset(self):
        queryset = GeneratedImage.objects.select_related("thread").all().order_by("-created_at")
        
        app_name = self.request.query_params.get("app_name")
        image_type = self.request.query_params.get("image_type")

        if app_name and app_name.strip().lower() != "all":
            queryset = queryset.filter(thread__app_name__iexact=app_name.strip())
        if image_type and image_type.strip().lower() != "all":
            queryset = queryset.filter(thread__image_type__iexact=image_type.strip())

        return queryset


class SelectImageView(APIView):
    """
    POST /api/images/{id}/select/
    Finalizes / toggles an image as chosen for download/library prominence.
    """
    def post(self, request, id):
        img = get_object_or_404(GeneratedImage, id=id)
        img.is_selected = True
        img.save(update_fields=["is_selected"])
        return Response({"success": True, "id": img.id, "is_selected": True})