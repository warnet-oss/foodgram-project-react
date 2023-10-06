from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Follow(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
    
    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural ='Подписки'
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name = 'unique_user_following'
                
            )
        ]
        
    def __str__(self):
        return f"Подписчик {self.user} - автор {self.following}"
    