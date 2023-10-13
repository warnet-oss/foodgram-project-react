from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followed_users',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural ='Подписки'
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.following}"
    