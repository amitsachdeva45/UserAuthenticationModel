from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.db.models.signals import post_save
from django.core.validators import RegexValidator


class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            username,
            password=password,

        )
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user

USERNAME_REGEX = "^[a-zA-Z0-9.+-]*$"

class MyUser(AbstractBaseUser):
    username = models.CharField(max_length=120,
                                validators=[
                                    RegexValidator(
                                        regex = USERNAME_REGEX,
                                        message="Username must be alphanumeric or contains:'. @ + -'",
                                        code='invalid_username'
                                )],
                                unique=True
                                )
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    zipcode = models.CharField(default="151204",max_length=120)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_admin

#################################################################################################
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    city = models.CharField(max_length=120,null=True,blank=True)

    def __str__(self):
        return str(self.user.username)

    def __unicode__(self):
        return str(self.user.username)


def post_save_user_model_receiver(sender,instance,created,*args,**kwargs):
    #It means if user model is created, then create profile of that user
    if created:
        try:
            Profile.objects.create(user=instance)
        except:
            pass

post_save.connect(post_save_user_model_receiver,sender=settings.AUTH_USER_MODEL)

