from django.contrib import admin

from .models import FavoriteRecipe, Ingredient, Recipe, ShoppingList, Tag


class RecipeIngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'title',
        'description',
        'cooking_time',
        'get_tags',
        'get_favorite_count'
    )
    inlines = (RecipeIngredientsInLine,)
    list_filter = ('author__email', 'tags', 'title')
    search_fields = ('author__email', 'title',)

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        list_ = [tag.name for tag in obj.tags.all()]
        return ', '.join(list_)

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)


@admin.register(FavoriteRecipe)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )


@admin.register(ShoppingList)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )