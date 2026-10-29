from django.db import models


class BrandProfile(models.Model):
    app_name = models.CharField(max_length=100, unique=True, default="")
    style_prompt = models.CharField(max_length=1000, default="")
    accent_color = models.CharField(max_length=20, default="#6c2bd9")
    
    # Preserved fields from initial migration
    name = models.CharField(max_length=150, blank=True, default="")
    description = models.TextField(blank=True, default="")
    primary_color = models.CharField(max_length=7, default="#000000")
    secondary_color = models.CharField(max_length=7, default="#FFFFFF")
    logo = models.ImageField(upload_to="brand_logos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name and self.app_name:
            self.name = self.app_name
        elif not self.app_name and self.name:
            self.app_name = self.name
        if self.accent_color and (not self.primary_color or self.primary_color == "#000000"):
            self.primary_color = self.accent_color[:7]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.app_name or self.name or f"Brand #{self.id}"


class GenerationThread(models.Model):
    app_name = models.CharField(max_length=100, default="")
    image_type = models.CharField(max_length=50, default="banner")
    width_px = models.IntegerField(default=1024)
    height_px = models.IntegerField(default=500)
    original_prompt = models.CharField(max_length=500, default="")
    
    # Preserved fields from initial migration
    brand_profile = models.ForeignKey(
        BrandProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="threads",
    )
    prompt = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.original_prompt and self.prompt:
            self.original_prompt = self.prompt[:500]
        elif not self.prompt and self.original_prompt:
            self.prompt = self.original_prompt
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Thread {self.id} ({self.app_name} - {self.image_type})"


class GeneratedImage(models.Model):
    thread = models.ForeignKey(
        GenerationThread,
        on_delete=models.CASCADE,
        related_name="images",
    )
    round_number = models.IntegerField(default=1)
    refinement_text = models.CharField(max_length=500, null=True, blank=True)
    template_used = models.CharField(max_length=50, null=True, blank=True)
    prompt_text = models.CharField(max_length=500, default="")
    image_url = models.CharField(max_length=500, blank=True, default="")
    parent_image = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refinements",
    )
    is_selected = models.BooleanField(default=False)
    
    # Preserved fields from initial migration
    image = models.ImageField(upload_to="generated_images/", blank=True, null=True)
    width = models.PositiveIntegerField(default=1024)
    height = models.PositiveIntegerField(default=500)
    prompt = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.prompt_text and self.prompt:
            self.prompt_text = self.prompt[:500]
        elif not self.prompt and self.prompt_text:
            self.prompt = self.prompt_text
        if not self.image_url and self.image:
            self.image_url = self.image.url
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image {self.id} [Round {self.round_number}] ({self.width}x{self.height})"