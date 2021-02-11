from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from blog.models import Post, File, Profile
import tempfile
import os
from django.conf import settings
from blog.tests.test_views import get_temporary_image
from django.core.files import File as djFile
from blog.templatetags.filters import get_basename, get_media_url

class TestFile(TestCase):

    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser')
        cls.user.set_password('12345')
        cls.user.save()
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        test_image = get_temporary_image(temp_file)
        temp_name = test_image.name
        test_image.close()
        os.rename(temp_name, os.path.join(tempfile.gettempdir(), 'test_file.jpg'))
        test_image = djFile(open(os.path.join(tempfile.gettempdir(), 'test_file.jpg'), 'rb'))
        cls.file = test_image

    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def tearDownClass(cls):
        cls.file.close()
        os.remove(os.path.join(tempfile.gettempdir(), cls.file.name))
        super().tearDownClass()

    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def test_files(self):
        self.client.login(username='testuser', password='12345')
        post = Post.objects.create(user=self.user, title='test', description='test')
        f = File.objects.create(post=post)
        f.file = self.file
        f.file.name = get_basename(self.file.name)
        f.save()
        # are test files saved in the right directory?
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'blog', 'testuser', f'{post.id}', os.path.basename(f.file.name))))
        post.delete()
        # are test files deleted on post deletion?
        self.assertFalse(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'blog', 'testuser', f'{post.id}', os.path.basename(f.file.name))))
        self.client.logout()

class TestProfile(TestCase):

    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser')
        cls.user.set_password('12345')
        cls.user.save()
        cls.files = []
        for i in range(2):
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            test_image = get_temporary_image(temp_file)
            temp_name = test_image.name
            test_image.close()
            os.rename(temp_name, os.path.join(tempfile.gettempdir(), f'test_file_{i}.jpg'))
            test_image = djFile(open(os.path.join(tempfile.gettempdir(), f'test_file_{i}.jpg'), 'rb'))
            cls.files.append(test_image)

    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def tearDownClass(cls):
        for f in cls.files:    
            f.close()
            os.remove(os.path.join(tempfile.gettempdir(), f.name))
        super().tearDownClass()

    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def test_profile_avatar(self):
        self.client.login(username='testuser', password='12345')
        profile = Profile.objects.create(user=self.user,
                                    phone='test',
                                    city='test', 
                                    description='Test')
        profile.photo = self.files[0]
        profile.photo.name = get_basename(self.files[0].name)
        profile.save()
        # is avatar saved in the right directory?
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'testuser', 'avatar', os.path.basename(self.files[0].name))))
        profile.photo = self.files[1]
        profile.photo.name = get_basename(self.files[1].name)
        profile.save()
        # is file deleted on avatar update?
        self.assertFalse(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'testuser', 'avatar', os.path.basename(self.files[0].name))))
        profile.delete()
        # are avatar files deleted on post deletion?
        self.assertFalse(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'testuser', 'avatar', os.path.basename(self.files[1].name))))
        self.client.logout()