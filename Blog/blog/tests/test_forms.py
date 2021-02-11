from django.test import TestCase, override_settings
from django.contrib.auth.models import User
import tempfile
import os
from blog.tests.test_views import get_temporary_image
from blog.forms import PostForm, PostAddListForm, FileForm, UserEditForm, ExtendedRegisterForm, ProfileForm
from django.core.files import File as djFile
from django.utils.datastructures import MultiValueDict

class TestForms(TestCase):

    test_files_num = 2

    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser')
        cls.user.set_password('12345')
        cls.user.save()
        cls.files = []
        for i in range(cls.test_files_num):
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            test_image = get_temporary_image(temp_file)
            temp_name = test_image.name
            test_image.close()
            os.rename(temp_name, os.path.join(tempfile.gettempdir(), f'test_posts_{i}.jpg'))
            test_image = djFile(open(os.path.join(tempfile.gettempdir(), f'test_posts_{i}.jpg'), 'rb'))
            cls.files.append(test_image)

    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def tearDownClass(cls):
        for f in cls.files:
            f.close()
            os.remove(os.path.join(tempfile.gettempdir(), f.name))
        super().tearDownClass()

    def setUp(self):
        for f in self.files:
            f.seek(0)

    def test_post_form(self):
        # these fields are supposed to be required
        post_form = PostForm({'title' : '', 'description' : ''})
        self.assertFalse(post_form.is_valid())
        post_form = PostForm({'title' : 'test', 'description' : 'test'})
        self.assertTrue(post_form.is_valid())

    def test_profile_form(self):
        # profile form field are all optional
        profile_form = ProfileForm({'city' : '', 'phone' : '', 'description' : '', 'photo' : None})
        self.assertTrue(profile_form.is_valid())

    def test_register_form(self):
        # register form field are optional too
        register_form = ExtendedRegisterForm({'username' : 'TestUser',
                                              'password1' : 'asdwvff544',
                                              'password2' : 'asdwvff544',
                                              'city' : '',
                                              'phone' : '',
                                              'description' : '',
                                              'photo' : None,
                                              'first_name' : '',
                                              'last_name' : ''})
        self.assertTrue(register_form.is_valid())

    def test_file_form(self):
        # file field is optional
        file_form = FileForm({}, {'files': []})
        self.assertTrue(file_form.is_valid())
        # and it's supposed to support multiple file selection
        file_form = FileForm({}, MultiValueDict({'files': self.files}))
        self.assertTrue(file_form.is_valid())

    def test_post_csv_form(self):
        # file field is required
        post_form = PostAddListForm({}, {'file': None})
        self.assertFalse(post_form.is_valid())
        # and it's not supposed to support multiple file selection
        post_form = PostAddListForm({}, {'file': self.files})
        self.assertFalse(post_form.is_valid())
        # but supposed to support one per time file selection
        post_form = PostAddListForm({}, {'file': self.files[0]})
        self.assertTrue(post_form.is_valid())
