from django.core.management.base import BaseCommand
from restaurants.models import FoodType, Category

class Command(BaseCommand):
    help = "Seed FoodTypes and global Categories"

    def handle(self, *args, **options):
        for ft in ["Vegetarian", "Non-Vegetarian"]:
            FoodType.objects.get_or_create(name=ft)
        for name in Category.GLOBAL_DEFAULTS:
            Category.objects.get_or_create(name=name, restaurant=None)
        self.stdout.write(self.style.SUCCESS("Seeded FoodTypes and global Categories."))