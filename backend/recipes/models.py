from django.db import models
from django.db.models import UniqueConstraint
from users.models import User


class Tag(models.Model):
    '''Теги'''
    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Код цвета тега', max_length=7, unique=True)
    slug = models.SlugField('slug тега', unique=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''Ингридиенты'''
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Система измерения', max_length=50)
    #  TODO Можно сделать choice поле и словарь.

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        # TODO МОжно добавить уникальность полям

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    '''Рецепты'''
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингридиенты',
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField('Название рецепта', max_length=200)
    image = models.ImageField(
        'Изображение блюда',
        upload_to='recipes/',
        null=True,
        blank=True,
        height_field=None,
        width_field=None,
        max_length=None,
    )
    text = models.TextField('Описание рецепта')
    cooking_time = models.PositiveIntegerField('Время приготовления в мин.',
                                               default=0,
                                               )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    '''Ингредиенты в рецепте'''
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингридиент',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField('Количество')

    class Meta:
        verbose_name = 'Ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'

    def __str__(self) -> str:
        return f'{self.recipe} {self.ingredient}'


class AbstractListGoods(models.Model):
    '''Абстрактная модель для корзины и избранного'''
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        constraints = [UniqueConstraint(
            fields=('user', 'recipe'), name='unique_names')]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Favorite(AbstractListGoods):
    '''Избранное'''

    class Meta:
        default_related_name = 'favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(AbstractListGoods):
    '''Списк покупок'''

    class Meta:
        default_related_name = 'shopping_list'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
