from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Назавание тега",
        max_length=255,
        unique=True,
    )
    
    color_code = models.CharField(
        verbose_name='Цветовой код',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^#[a-fA-F0-9]{6}$",
                message="Поле должно содержать HEX-код цвета"
            ),
        ]
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=255,
        unique=True,
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plura = 'Тег'
    
    
class Recipe(models.Model):
    autho = models.ForeignKey(
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
        upload_to = "recipe_image/",
        
    )
    
    description = models.TextField(
        verbose_name='Текстовое описание',
        
    )
    
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Ингредиенты',
        through='RecipeIngredient',
    )
    
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Теги',
    )
    
    cooking_time = models.PositiveIntegerField(
        verbose_name = 'Время приготовления в минутах',
        validators = [MinLengthValidator(1,"Время от 1 минуты")]
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикаций", auto_now_add=True
    )
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ("-pud_date")
    
    def __str__(self):
        return self.title
    
    
class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название ингридиента",
        max_length=255,
        unique=True,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения", max_length=255
    )
    
    class Mate:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        
    def __str__(self):
        return f"{self.name}, {self.measurement_unit}. "
        
    
class RecipeIngredient(models.Model):
    recipe =models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    
    amout = models.PositiveIntegerField(
        default =1,
        verbose_name = 'Количество',
        validators = [ 
                      MinLengthValidator(1,'Должны быть ингредиенты')
                      ],
    )
    
    class Meta:
        verbose_name = "Ингридиент для рецепта"
        verbose_name_plural = "Ингридиенты для рецепта"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"), name="uniqe_ingredient"
            )
        ]
    
    def __str__(self):
        return f"{self.ingredient} - {self.amout}"
    
    