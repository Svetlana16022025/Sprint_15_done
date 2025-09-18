from rest_framework import serializers

from reviews.models import Category, Genre, Title, Review, Comment


MIN_SCORE = 1
MAX_SCORE = 10


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров"""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведений"""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(
        read_only=True,
        allow_null=True,
        label='Рейтинг'
    )

    class Meta:
        model = Title
        fields = '__all__'
        labels = {
            'name': 'Название',
            'year': 'Год выпуска',
            'description': 'Описание',
            'category': 'Категория',
            'genre': 'Жанр',
        }


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания произведений"""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        label='Категория'
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        label='Жанры'
    )

    class Meta:
        model = Title
        fields = '__all__'
        labels = {
            'name': 'Название',
            'year': 'Год выпуска',
            'description': 'Описание',
        }


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов"""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        label='Автор',
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        labels = {
            'text': 'Текст отзыва',
            'score': 'Оценка',
            'pub_date': 'Дата публикации',
        }

    def validate_score(self, value):
        if value < MIN_SCORE or value > MAX_SCORE:
            raise serializers.ValidationError(
                f'Оценка должна быть от {MIN_SCORE} до {MAX_SCORE}'
            )
        return value

    def validate(self, data):
        if self.context['request'].method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            user = self.context['request'].user

            if Review.objects.filter(title_id=title_id, author=user).exists():
                raise serializers.ValidationError(
                    "Вы уже оставили отзыв на это произведение"
                )

        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев"""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        label='Автор'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        labels = {
            'text': 'Текст комментария',
            'pub_date': 'Дата публикации',
        }
