from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 🔥 Ajouté pour lier la dépense à l'utilisateur
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=50)  # ✨ Saisie libre ici
    date = models.DateField()

    def __str__(self):
        return f"{self.date} – {self.description} ({self.amount} {self.get_user_currency()})"

    def get_user_currency(self):
        try:
            return self.user.profile.currency
        except:
            return '€'  # devise par défaut si pas de profil

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    CURRENCY_CHOICES = [
        ('€', 'Euro (€)'),
        ('$', 'Dollar ($)'),
        ('FCFA', 'Franc CFA'),
        ('£', 'Livre (£)'),
        ('¥', 'Yen (¥)'),
    ]

    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='FCFA')

    def __str__(self):
        return f"Profil de {self.user.username}"

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()