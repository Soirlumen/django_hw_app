from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import CustomUser, StudentProfile, TeacherProfile
from django.conf import settings

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance,created,**kwargs):
    if created:
        if instance.role=='student':
            StudentProfile.objects.create(user=instance)
        elif instance.role=='teacher':
            TeacherProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def set_admin_role_for_superuser(sender, instance, created, **kwargs):
    if created and instance.is_superuser and instance.role != 'admin':
        instance.role = 'admin'
        instance.save()

@receiver(pre_save,sender=settings.AUTH_USER_MODEL)
def set_superuser_if_admin_role(sender, instance,**kwargs):
    instance.is_superuser=True
    instance.is_staff=True