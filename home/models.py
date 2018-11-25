from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.
class Book(models.Model):
    title=models.CharField(max_length=50)
    author=models.CharField(max_length=50)
    genre=models.CharField(max_length=50)
    description=models.TextField(null=True)
    mrp=models.PositiveIntegerField()
    rating=models.FloatField(default=0.0)
    class Meta:
        ordering=('title',)
    def __str__(self):
        return self.title+" by "+self.author

class BookInstance(models.Model):
    book=models.ForeignKey(Book,on_delete=models.CASCADE)
    b_date=models.DateField(null=True)
    status=models.BooleanField(default=False)
    borrower=models.ForeignKey('Profile',related_name='borrowed',null=True,on_delete=models.SET_NULL)
    uploader=models.ForeignKey('Profile',related_name='uploaded',null=True,on_delete=models.SET_NULL)
    def __str__(self):
        return self.book_id+" , "+str(self.b_date)
    
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    balance=models.FloatField(default=0.0)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Rating(models.Model):
    user=models.OneToOneField(Profile,on_delete=models.CASCADE)
    book=models.OneToOneField(Book,on_delete=models.CASCADE,related_name='rating_set')
    rating=models.PositiveIntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)])