import io
import os
import random
import time
import urllib.parse
import requests
from typing import List, Tuple, Optional
from PIL import Image
from django.conf import settings
from .models import BrandProfile, GenerationThread, GeneratedImage
from .templates import apply_template, TEMPLATE_KEYS


import logging
logger = logging.getLogger(__name__)


class ImageGenerationError(Exception):
    """Custom exception raised when external AI image generation fails."""
    pass


def get_ai_provider() -> str:
    """Determine AI provider from environment or auto-detect."""
    explicit_provider = os.getenv("AI_PROVIDER", "").strip().lower()
    if explicit_provider in ("stability", "gemini", "openai", "pollinations"):
        return explicit_provider
    if os.getenv("STABILITY_API_KEY"):
        return "stability"
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    # Default to Pollinations (free real generative AI diffusion)
    return "pollinations"


def _generate_with_pollinations(prompt: str, seed: int, width: int = 1024, height: int = 1024) -> Image.Image:
    """Generate image using Pollinations.ai diffusion API."""
    encoded_prompt = urllib.parse.quote(prompt)
    # Most diffusion models generate best at native ~1024 or 768
    gen_w = min(1024, max(512, width))
    gen_h = min(1024, max(512, height))
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={gen_w}&height={gen_h}&seed={seed}&nologo=true&enhance=false"
    
    headers = {
        "User-Agent": "FS7-ImageGenPlatform/1.0 (Mozilla/5.0)",
        "Accept": "image/jpeg,image/png,image/*",
    }
    
    response = requests.get(url, headers=headers, timeout=45)
    if response.status_code != 200:
        raise ImageGenerationError(f"Pollinations AI returned HTTP {response.status_code}: {response.text[:200]}")
    
    try:
        img = Image.open(io.BytesIO(response.content))
        img.load()
        return img
    except Exception as e:
        raise ImageGenerationError(f"Failed to decode generated image binary: {str(e)}")


def _generate_with_openai(prompt: str, api_key: str, width: int = 1024, height: int = 1024) -> Image.Image:
    """Generate image using OpenAI DALL-E."""
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Pick supported DALL-E resolution
    payload = {
        "model": os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3"),
        "prompt": prompt[:1000],
        "n": 1,
        "size": "1024x1024",
        "response_format": "b64_json",
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    if response.status_code != 200:
        raise ImageGenerationError(f"OpenAI API error {response.status_code}: {response.text[:250]}")
    
    import base64
    data = response.json()
    b64_data = data["data"][0].get("b64_json")
    if not b64_data:
        raise ImageGenerationError("No image data returned from OpenAI API")
    
    img_bytes = base64.b64decode(b64_data)
    img = Image.open(io.BytesIO(img_bytes))
    img.load()
    return img


def _generate_with_stability(prompt: str, api_key: str) -> Image.Image:
    """Generate image using Stability AI API."""
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "text_prompts": [{"text": prompt[:1000], "weight": 1.0}],
        "cfg_scale": 7,
        "samples": 1,
        "steps": 30,
    }
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    if response.status_code != 200:
        raise ImageGenerationError(f"Stability AI error {response.status_code}: {response.text[:250]}")
    
    import base64
    data = response.json()
    artifacts = data.get("artifacts", [])
    if not artifacts:
        raise ImageGenerationError("No artifacts returned from Stability AI")
    
    img_bytes = base64.b64decode(artifacts[0]["base64"])
    img = Image.open(io.BytesIO(img_bytes))
    img.load()
    return img


def _generate_with_gemini(prompt: str, api_key: str, width: int = 1024, height: int = 1024) -> Image.Image:
    """Generate image using Google Gemini / Imagen 3 API."""
    import base64
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
    headers = {"Content-Type": "application/json"}

    # Map target dimensions to closest supported aspect ratio
    aspect = "1:1"
    ratio = width / height if height > 0 else 1.0
    if ratio >= 1.5:
        aspect = "16:9"
    elif ratio >= 1.2:
        aspect = "4:3"
    elif ratio <= 0.67:
        aspect = "9:16"
    elif ratio <= 0.85:
        aspect = "3:4"

    payload = {
        "instances": [{"prompt": prompt[:1000]}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect,
            "outputOptions": {"mimeType": "image/png"},
        },
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    if response.status_code != 200:
        raise ImageGenerationError(f"Gemini/Imagen API error {response.status_code}: {response.text[:250]}")

    data = response.json()
    predictions = data.get("predictions", [])
    if not predictions or "bytesBase64Encoded" not in predictions[0]:
        raise ImageGenerationError("No image data returned from Gemini/Imagen API")

    img_bytes = base64.b64decode(predictions[0]["bytesBase64Encoded"])
    img = Image.open(io.BytesIO(img_bytes))
    img.load()
    return img


def generate_single_ai_image(prompt: str, width: int = 1024, height: int = 1024, seed: Optional[int] = None) -> Image.Image:
    """Dispatches to configured AI provider to produce a single genuine AI image."""
    provider = get_ai_provider()
    actual_seed = seed if seed is not None else random.randint(10000, 9999999)

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            logger.warning("GEMINI_API_KEY is not configured. Falling back to Pollinations diffusion.")
            return _generate_with_pollinations(prompt, seed=actual_seed, width=width, height=height)
        try:
            return _generate_with_gemini(prompt, api_key, width, height)
        except Exception as e:
            logger.warning(f"Gemini API failed: {e}. Falling back to Pollinations diffusion.")
            return _generate_with_pollinations(prompt, seed=actual_seed, width=width, height=height)
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            logger.warning("OPENAI_API_KEY is not configured. Falling back to Pollinations diffusion.")
            return _generate_with_pollinations(prompt, seed=actual_seed, width=width, height=height)
        try:
            return _generate_with_openai(prompt, api_key, width, height)
        except Exception as e:
            logger.warning(f"OpenAI API failed: {e}. Falling back to Pollinations diffusion.")
            return _generate_with_pollinations(prompt, seed=actual_seed, width=width, height=height)
    elif provider == "stability":
        api_key = os.getenv("STABILITY_API_KEY", "").strip()
        if not api_key:
            logger.warning("STABILITY_API_KEY is not configured. Falling back to Pollinations diffusion.")
            return _generate_with_pollinations(prompt, seed=actual_seed, width=width, height=height)
        try:
            return _generate_with_stability(prompt, api_key)
        except Exception as e:
            logger.warning(f"Stability AI failed: {e}. Falling back to Pollinations diffusion.")
            return _generate_with_pollinations(prompt, seed=actual_seed, width=width, height=height)
    else:
        return _generate_with_pollinations(prompt, seed=actual_seed, width=width, height=height)


def build_effective_prompt(base_prompt: str, brand_profile: Optional[BrandProfile] = None, refinement_text: Optional[str] = None) -> str:
    """
    Constructs the effective prompt sent to the AI engine.
    - Prepends brand style snippet.
    - Appends refinement instruction if present.
    """
    parts = []
    if brand_profile:
        style_snippet = f"Brand: {brand_profile.app_name}. Style guidelines: {brand_profile.style_prompt}."
        parts.append(style_snippet)

    parts.append(f"Subject: {base_prompt.strip()}")

    if refinement_text:
        parts.append(f"Refinement requirements: {refinement_text.strip()}")

    parts.append("Commercial marketing quality, ultra-detailed, professional lighting, centered composition.")
    return " ".join(parts)


def process_and_save_image(
    raw_img: Image.Image,
    thread: GenerationThread,
    round_number: int,
    effective_prompt: str,
    template_name: Optional[str] = None,
    refinement_text: Optional[str] = None,
    parent_image: Optional[GeneratedImage] = None,
    accent_color: str = "#3377FF",
) -> GeneratedImage:
    """
    Composites the raw AI image through the parametric template engine,
    creates the GeneratedImage record, saves the file locally according to
    FS-7 naming convention: {image_type}_{width}x{height}_{id}.png,
    and updates the database record.
    """
    target_w = thread.width_px
    target_h = thread.height_px
    image_type = thread.image_type

    # 1. First create the database record to get an authoritative ID
    img_record = GeneratedImage.objects.create(
        thread=thread,
        round_number=round_number,
        refinement_text=refinement_text,
        template_used=template_name or "",
        prompt_text=effective_prompt[:500],
        prompt=effective_prompt,
        width=target_w,
        height=target_h,
        parent_image=parent_image,
        is_selected=False,
    )

    # 2. Composite through template engine
    composited, chosen_template = apply_template(
        photo=raw_img,
        target_width=target_w,
        target_height=target_h,
        template_name=template_name,
        accent_color=accent_color,
        headline_text=thread.original_prompt[:60],
        app_name=thread.app_name,
    )

    # 3. Save file using mandatory FS-7 naming convention:
    # {image_type}_{width}x{height}_{id}.png
    clean_type = image_type.lower().replace(" ", "_")
    filename = f"{clean_type}_{target_w}x{target_h}_{img_record.id}.png"
    
    # Target directory inside MEDIA_ROOT
    media_dir = os.path.join(settings.MEDIA_ROOT, "generated")
    os.makedirs(media_dir, exist_ok=True)
    full_path = os.path.join(media_dir, filename)

    composited.save(full_path, format="PNG", optimize=True)

    # Relative URL
    rel_url = f"/media/generated/{filename}"
    img_record.image_url = rel_url
    img_record.template_used = chosen_template
    # Also set django ImageField path relative to MEDIA_ROOT
    img_record.image.name = f"generated/{filename}"
    img_record.save(update_fields=["image_url", "template_used", "image"])

    return img_record


def generate_round_variations(
    thread: GenerationThread,
    round_number: int,
    effective_prompt: str,
    brand_profile: Optional[BrandProfile] = None,
    refinement_text: Optional[str] = None,
    parent_image: Optional[GeneratedImage] = None,
) -> List[GeneratedImage]:
    """
    Generates exactly three genuine image variations, applies distinct parametric
    templates to each, and saves them to MySQL and the filesystem.
    """
    accent_color = brand_profile.accent_color if brand_profile else "#3377FF"
    
    # Select 3 distinct templates from our parametric engine
    available_templates = list(TEMPLATE_KEYS)
    random.shuffle(available_templates)
    templates_for_round = available_templates[:3]
    if len(templates_for_round) < 3:
        templates_for_round = TEMPLATE_KEYS[:3]

    results = []
    # Generate 3 variations with distinct seeds
    base_seed = random.randint(100000, 999999)
    for i in range(3):
        seed = base_seed + i * 1337
        # Slight variation in prompt emphasis for genuine variety
        var_prompt = f"{effective_prompt} [Perspective variation {i+1}]"
        raw_img = generate_single_ai_image(
            prompt=var_prompt,
            width=thread.width_px,
            height=thread.height_px,
            seed=seed,
        )
        
        saved_record = process_and_save_image(
            raw_img=raw_img,
            thread=thread,
            round_number=round_number,
            effective_prompt=effective_prompt,
            template_name=templates_for_round[i],
            refinement_text=refinement_text,
            parent_image=parent_image,
            accent_color=accent_color,
        )
        results.append(saved_record)

    return results
