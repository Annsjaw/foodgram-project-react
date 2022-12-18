from django.db import models
from users.models import User

UNIT = {'kg': 'кг',
        'g': 'г',
        'L': 'Л',
        'ml': 'мл'
        }


class Tag(models.Model):
    name = models.CharField('Название', max_length=200)
    color = models.CharField('Код цвета тега', max_length=7)
    slug = models.SlugField('slug тега', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Система измерения', max_length=50)
    #  TODO Можно сделать choice поле и словарь.

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes',
    )
    ingridients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField(
        'Изображение блюда',
        upload_to='recipes/',
        null=True,
        blank=True,
        height_field=None,
        width_field=None,
        max_length=None,
    )
    text = models.TextField('Текст рецепта')
    cooking_time = models.PositiveIntegerField('Время приготовления в мин.')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name
