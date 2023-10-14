from django.contrib.auth import get_user_model
from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, serializers

from recipes.models import (FavoriteRecipe,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow

User = get_user_model()


class GetIsSubscribedMixin:

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj.id).exists()


class GetIngredientsMixin:

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("ingredients_amount__amount"),
        )


class CustomUserSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user,
                                     author=obj.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'password')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class GetIngredientRecipeSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    def get_amount(self, obj):
        return obj.amount


class GetRecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=request.user,
                                             recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=request.user,
                                           recipe=obj.id).exists()

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        serializer = GetIngredientRecipeSerializer(ingredients, many=True)
        return serializer.data


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShortIngredientSerializerForRecipe(serializers.ModelSerializer):

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class PostRecipeSerializer(serializers.ModelSerializer):

    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = ShortIngredientSerializerForRecipe(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    def validate_tags(self, tags):
        if not tags:
            raise exceptions.ValidationError(
                'Должен быть хотя бы один тег.')
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise exceptions.ValidationError(
                'Должен быть хотя бы один ингредиент.')

        ingredients_id_list = [ingredient['id'] for ingredient in ingredients]
        for ingredient_id in ingredients_id_list:
            if ingredients_id_list.count(ingredient_id) > 1:
                raise exceptions.ValidationError(
                    'У рецепка не может быть два одинаковых игредиента.')
        return ingredients

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise exceptions.ValidationError(
                'Минимальное время приготовления 1 минута.')
        return cooking_time

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        recipe_ingredients = []

        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient_instance = ingredient['id']
            ingredient = get_object_or_404(Ingredient, pk=ingredient_instance)

            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()

            for ingredient in ingredients:
                amount = ingredient['amount']
                ingredient_instance = ingredient['id']
                ingredient = get_object_or_404(Ingredient,
                                               pk=ingredient_instance)

                RecipeIngredient.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=amount
                )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = GetRecipeSerializer(
            instance
        )
        return serializer.data

    class Meta:
        model = Recipe
        exclude = ('created',)


class SubscriptionSerializer(serializers.ModelSerializer):

    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        return True

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name',
                  'is_subscribed', 'recipes', "recipes", 'recipes_count')
