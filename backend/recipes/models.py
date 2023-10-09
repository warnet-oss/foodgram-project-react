from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        null=True,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Поле должно содержать HEX-код выбранного цвета.'
            )
        ]

    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=200,
        unique=True,
        null=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


    slug = models.SlugField(
        verbose_name='Slug',
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название ингредиента",
        max_length=255,
        unique=True,
    )

    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=255
    )

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )

    title = models.CharField(
        verbose_name="Название",
        max_length=255,
        unique=True,
    )

    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="recipe_image/",
    )

    description = models.TextField(
        verbose_name='Текстовое описание',
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )

    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinLengthValidator(1, "Время от 1 минуты")]
    )

    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ("-pub_date",)

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )

    amount = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество',
        validators=[
            MinLengthValidator(1, 'Должно быть хотя бы 1 ингредиент')
        ],
    )

    def __str__(self):
        return f"{self.ingredient} - {self.amount}"

    class Meta:
        verbose_name = "Ингредиент для рецепта"
        verbose_name_plural = "Ингредиенты для рецепта"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"), name="unique_ingredient"
            )
        ]

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_followers',
        verbose_name='Подписчик'
    )

    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_followings',
        verbose_name='Автор'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} подписан на {self.following}"

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following_recipes'
            )
        ]

class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_recipes",
        verbose_name="Пользователь"
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Рецепт"
    )

    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.recipe.name}"

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        ordering = ("-date_added",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_user_recipe_favorite"
            )
        ]

class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_lists",  
        verbose_name="Пользователь"
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="added_to_shopping_lists",
        verbose_name="Рецепт"
    )

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - Список покупок для {self.recipe.title}"

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        ordering = ("-date_created",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_user_recipe_shoppinglist"
            )
        ]