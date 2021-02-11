from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from blog.models import Post, File, Profile
from datetime import date, timedelta
import tempfile
from PIL import Image
import os
from django.urls import reverse
from django.conf import settings
from blog.templatetags.filters import get_basename, get_media_url
from csv import writer, QUOTE_MINIMAL
from django.core.files import File as djFile

def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0)
    image = Image.new("RGB", size, color)
    image.save(temp_file, 'jpeg')
    return temp_file

def is_sorted(l, asc=True):
    if asc:
        return all(a <= b for a, b in zip(l, l[1:]))
    else:
        return all(a >= b for a, b in zip(l, l[1:]))

class TestLoginLogout(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser')
        cls.user.set_password('12345')
        cls.user.save()
        cls.post = Post.objects.create(title='Test', description='Test', user=cls.user)

    def test_login(self):
        response = self.client.post(reverse('login'), {'username' : 'testuser', 'password' : '12345'})
        # are we actually redirected to LOGIN_REDIRECT_URL?
        self.assertRedirects(response, reverse('blog_list'))
        # are we authenticated as testuser?
        response = self.client.get(reverse('blog_list'))
        self.assertContains(response, '<span>Добро пожаловать, <strong>testuser</strong> |</span>')
        # the same header is supposed to be rendered in detail view
        response = self.client.get(reverse('post_detail', args = [self.post.id]))
        self.assertContains(response, '<span>Добро пожаловать, <strong>testuser</strong> |</span>')
        self.client.logout()
        response = self.client.post(reverse('login'), {'username' : 'testuser', 'password' : '12345', 'next' : reverse('profile')})
        # are we actually redirected to the url required by next?
        self.assertRedirects(response, reverse('profile'))

    def test_logout(self):
        response = self.client.get(reverse('logout'))
        # are we actually redirected?
        self.assertRedirects(response, reverse('blog_list'))
        # are we NOT authenticated as testuser now?
        response = self.client.get(reverse('blog_list'))
        self.assertContains(response, '<span>Вы не вошли |</span>')
        # the same header is supposed to be rendered in detail view
        response = self.client.get(reverse('post_detail', args = [self.post.id]))
        self.assertContains(response, '<span>Вы не вошли |</span>')

class TestPostListDetail(TestCase):
    
    NUMBER_OF_POSTS = 10
    test_files_num = 2
    
    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def setUpTestData(cls):
        cls.user, cls.user2 = User.objects.create_user(username='testuser'), User.objects.create_user(username='testuser2')
        cls.user.set_password('12345')
        cls.user2.set_password('12345')
        cls.user.save()
        cls.user2.save()
        cls.files = []
        for i in range(cls.test_files_num):
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            test_image = get_temporary_image(temp_file)
            temp_name = test_image.name
            test_image.close()
            os.rename(temp_name, os.path.join(tempfile.gettempdir(), f'test_posts_{i}.jpg'))
            test_image = open(os.path.join(tempfile.gettempdir(), f'test_posts_{i}.jpg'), 'rb')
            cls.files.append(test_image)
        for i in range(cls.NUMBER_OF_POSTS):
            Post.objects.create(user = cls.user, title = f'Title {i}', description = f'Description {i}')

    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def tearDownClass(cls):
        for f in cls.files:
            f.close()
            os.remove(os.path.join(tempfile.gettempdir(), f.name))
        super().tearDownClass()
    
    def test_post_list(self):
        response = self.client.get(reverse('blog_list'))
        # just check whether the view is found on our server an all is ok with the template used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_list.html')
        # is the post list we've just created sent via context correctly?
        self.assertTrue(len(response.context['post_list']) == self.NUMBER_OF_POSTS)
        # is post list sorted by creation date descending?
        self.assertTrue(is_sorted([post.published_at for post in response.context['post_list']], asc=False))
        for post in Post.objects.all():
            # since we are not authenticated this form is supposed to be unavailable
            self.assertNotContains(response, f'<form action="{reverse("post_edit", args=[post.id])}" method="get" class="edit-btn-form">')
        self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('blog_list'))
        for post in Post.objects.all():
            # since we are authenticated not as post author this form is supposed to be unavailable too
            self.assertNotContains(response, f'<form action="{reverse("post_edit", args=[post.id])}" method="get" class="edit-btn-form">')        
        self.client.logout()
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('blog_list'))
        for post in Post.objects.all():
            # since we are authenticated as post author now this form is supposed to be available
            self.assertContains(response, f'<form action="{reverse("post_edit", args=[post.id])}" method="get" class="edit-btn-form">')
        self.client.logout()

    def test_post_list_filter(self):
        test_date = date.today()
        # does our filtration mechanism work correctly?
        response = self.client.get(reverse('blog_list'), {'date' : test_date.strftime('%Y-%m-%d')})
        self.assertTrue(len(response.context['post_list']) == self.NUMBER_OF_POSTS)
        test_date = date.today() - timedelta(days = 2)
        # server is not supposed to answer with any posts with creation date other than today 
        # (and maybe yesterday if we are running our tests just right at 00:00)
        response = self.client.get(reverse('blog_list'), {'date' : test_date.strftime('%Y-%m-%d')})
        self.assertTrue(len(response.context['post_list']) == 0)

    def test_post_detail(self):
        self.client.login(username='testuser', password='12345')
        self.client.post(reverse('post_create'), {'title' : 'Test', 'description' : 'Test', 'files' : self.files})
        post = Post.objects.get(title='Test')
        response = self.client.get(reverse('post_detail', args = [post.id]))
        # as always are these view and template found?
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')
        # since we are authenticated as post author this form is supposed to be available
        self.assertContains(response, f'<form action="{reverse("post_edit", args=[post.id])}" method="get" class="edit-btn-form">')
        self.client.logout()
        self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('post_detail', args = [post.id]))
        # ...but not now
        self.assertNotContains(response, f'<form action="{reverse("post_edit", args=[post.id])}" method="get" class="edit-btn-form">')
        self.client.logout()
        response = self.client.get(reverse('post_detail', args = [post.id]))
        # ...and not now
        self.assertNotContains(response, f'<form action="{reverse("post_edit", args=[post.id])}" method="get" class="edit-btn-form">')
        # are test files available?
        for f in self.files:
            self.assertContains(response, f'<img src="{get_media_url("blog/testuser/" + str(post.id) + "/" + get_basename(f.name))}" alt="{get_basename(f.name)}" class="img">')
        post.delete()

class TestPostCreateEdit(TestCase):

    test_files_num = 2
    csv_rows = 5

    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser')
        cls.user.set_password('12345')
        cls.user.save()
        cls.user2 = User.objects.create_user(username='testuser2')
        cls.user2.set_password('12345')
        cls.user2.save()
        cls.files = []
        csv_file = tempfile.NamedTemporaryFile(mode='w', newline='', delete=False)
        csv_writer = writer(csv_file, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL)
        for i in range(cls.csv_rows):
            csv_writer.writerow([f'Title{i}', f'Description{i}'])
        temp_name = csv_file.name
        csv_file.close()
        os.rename(temp_name, os.path.join(tempfile.gettempdir(), 'test_csv.csv'))
        csv_file = open(os.path.join(tempfile.gettempdir(), 'test_csv.csv'), 'rb')
        cls.csv_file = csv_file
        for i in range(cls.test_files_num):
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            test_image = get_temporary_image(temp_file)
            temp_name = test_image.name
            test_image.close()
            os.rename(temp_name, os.path.join(tempfile.gettempdir(), f'test_posts_{i}.jpg'))
            test_image = open(os.path.join(tempfile.gettempdir(), f'test_posts_{i}.jpg'), 'rb')
            cls.files.append(test_image)

    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def tearDownClass(cls):
        for f in cls.files:
            f.close()
            os.remove(os.path.join(tempfile.gettempdir(), f.name))
        cls.csv_file.close()
        os.remove(os.path.join(tempfile.gettempdir(), cls.csv_file.name))
        super().tearDownClass()

    def setUp(self):
        for f in self.files:
            f.seek(0)

    def test_post_create_edit_no_login(self):
        response = self.client.get(reverse('post_create'))
        # since we are not authenticated we are supposed to be redirected to login page
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('post_create'))
        response = self.client.get(reverse('post_add_list'))
        # the same here
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('post_add_list'))
        self.client.login(username='testuser', password='12345')
        self.client.post(reverse('post_create'), {'title' : 'Test', 'description' : 'Test', 'files' : self.files})
        post = Post.objects.get(title='Test')
        self.client.logout()
        response = self.client.get(reverse('post_edit', args=[post.id]))
        # the same here
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('post_edit', args=[post.id]))
        post.delete()

    def test_post_edit_invalid_user(self):
        self.client.login(username='testuser2', password='12345')
        self.client.post(reverse('post_create'), {'title' : 'Test_edit2', 'description' : 'Test', 'files' : self.files})
        post = Post.objects.get(title='Test_edit2')
        self.client.logout()
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('post_edit', args=[post.id]))
        # since we are not the post author server should return 403 status code
        self.assertEqual(response.status_code, 403)
        post.delete()

    def test_post_create(self):
        self.client.login(username='testuser', password='12345')
        # as always are these view and template found?
        response = self.client.get(reverse('post_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/create_edit_post.html')
        # is post creation mechanism working?
        response = self.client.post(reverse('post_create'), {'title' : 'Test', 'description' : 'Test', 'files' : self.files})
        self.assertRedirects(response, reverse('blog_list'))
        # view is supposed to create new post object
        self.assertTrue(Post.objects.filter(title='Test', description='Test').exists())
        post = Post.objects.get(title='Test')
        post.delete()
        self.client.logout()

    def test_post_edit(self):
        self.client.login(username='testuser', password='12345')
        # as always are these view and template found?
        self.client.post(reverse('post_create'), {'title' : 'Test_edit', 'description' : 'Test', 'files' : self.files[1:]})
        post = Post.objects.get(title='Test_edit')
        # as always are these view and template found?
        response = self.client.get(reverse('post_edit', args=[post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/create_edit_post.html')
        # is given data used by view?
        self.assertTrue(response.context['post_form'].initial['title'] == 'Test_edit')
        self.assertTrue(response.context['post_form'].initial['description'] == 'Test')
        # are attached files displayed correctly?
        for f in post.files.all():
            self.assertContains(response, f'<a href="{reverse("post_edit", args=[post.id])}?delete={f.id}" class="file-delete-btn"></a>')
        test_file_id = post.files.all()[0].id
        # does delete/restore mechanics work?
        response = self.client.get(f'{reverse("post_edit", args=[post.id])}?delete={test_file_id}')
        self.assertContains(response, f'<a href="{reverse("post_edit", args=[post.id])}?restore={test_file_id}" class="file-restore-btn"></a>')
        response = self.client.get(f'{reverse("post_edit", args=[post.id])}?restore={test_file_id}')
        self.assertContains(response, f'<a href="{reverse("post_edit", args=[post.id])}?delete={test_file_id}" class="file-delete-btn"></a>')
        # now delete this file from the post
        f = File.objects.get(id=test_file_id)
        f.on_delete = True
        f.save()
        # ...change other fields and attach new file
        response = self.client.post(reverse('post_edit', args=[post.id]), {'title' : 'Test_after_edit', 'description' : 'Test_after_edit', 'files' : self.files[0]})
        # we are supposed to be redirected to details
        self.assertRedirects(response, reverse('post_detail', args=[post.id]))
        post = Post.objects.get(id=post.id)
        # was it actually changed?
        self.assertTrue(post.title == 'Test_after_edit')
        self.assertTrue(post.description == 'Test_after_edit')
        # test file object is supposed to be deleted now
        self.assertFalse(File.objects.filter(id=test_file_id).exists())
        # as well as the file itself
        self.assertFalse(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'blog', 'testuser', f'{post.id}', os.path.basename(f.file.name))))
        # but new file should exist now
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'blog', 'testuser', f'{post.id}', os.path.basename(self.files[0].name))))
        post.delete()
        self.client.logout()

    def test_add_csv(self):
        self.client.login(username='testuser', password='12345')
        # as always are these view and template found?
        response = self.client.get(reverse('post_add_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/create_edit_post.html')
        response = self.client.post(reverse('post_add_list'), {'file' : self.csv_file})
        # we are supposed to be redirected to post list
        self.assertRedirects(response, reverse('blog_list'))
        for i in range(self.csv_rows):
            # are posts actually added?
            self.assertTrue(Post.objects.filter(title=f'Title{i}', description=f'Description{i}').exists())

class TestRegisterView(TestCase):

    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def setUpTestData(cls):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        test_image = get_temporary_image(temp_file)
        temp_name = test_image.name
        test_image.close()
        os.rename(temp_name, os.path.join(tempfile.gettempdir(), 'test_photo.jpg'))
        test_image = open(os.path.join(tempfile.gettempdir(), 'test_photo.jpg'), 'rb')
        cls.photo = test_image

    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def tearDownClass(cls):
        cls.photo.close()
        os.remove(os.path.join(tempfile.gettempdir(), cls.photo.name))
        super().tearDownClass()

    def setUp(self):
        self.photo.seek(0)

    def test_register(self):
        # as always are these view and template found?
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/register.html') 
        response = self.client.post(reverse('register'), {'username' : 'Test', 
                                                        'password1' : 'awdrom32', 
                                                        'password2' : 'awdrom32', 
                                                        'first_name' : 'test', 
                                                        'last_name' : 'test',
                                                        'phone' : 'test',
                                                        'city' : 'test', 
                                                        'description' : 'Test', 
                                                        'photo' : self.photo})
        # we are supposed to be redirected to post list
        self.assertRedirects(response, reverse('blog_list'))
        # were user and profile objects created?
        self.assertTrue(User.objects.filter(username='Test', first_name='test', last_name='test').exists())
        user = User.objects.get(username='Test')
        self.assertTrue(Profile.objects.filter(user=user, phone='test', city='test', description='Test').exists())
        # are we authenticated as Test?
        response = self.client.get(reverse('blog_list'))
        self.assertContains(response, '<span>Добро пожаловать, <strong>Test</strong> |</span>')
        user.delete()

class TestProfileView(TestCase):

    test_files_num = 2

    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser')
        cls.user.set_password('12345')
        cls.user.save()
        cls.photos = []
        for i in range(cls.test_files_num):
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            test_image = get_temporary_image(temp_file)
            temp_name = test_image.name
            test_image.close()
            os.rename(temp_name, os.path.join(tempfile.gettempdir(), f'test_photo_{i}.jpg'))
            test_image = djFile(open(os.path.join(tempfile.gettempdir(), f'test_photo_{i}.jpg'), 'rb'))
            cls.photos.append(test_image)

    @classmethod
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def tearDownClass(cls):
        for f in cls.photos:
            f.close()
            os.remove(os.path.join(tempfile.gettempdir(), f.name))
        super().tearDownClass()

    def setUp(self):
        for f in self.photos:
            f.seek(0)

    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def test_profile_create_edit_no_login(self):
        response = self.client.get(reverse('profile'))
        # since we are not authenticated we are supposed to be redirected to login page
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('profile'))
        response = self.client.get(reverse('profile_edit'))
        # the same here
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('profile_edit'))

    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def test_profile(self):
        self.client.login(username='testuser', password='12345')
        # as always are these view and template found?
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/user_detail.html')
        # photo should not be rendered since we haven't created profile instance 
        photo_media_url = get_media_url('testuser/avatar/' + get_basename(self.photos[0].name))
        self.assertNotContains(response, f'<img src="{photo_media_url}" alt="testuser" class="profile-photo">')
        profile = Profile.objects.create(user=self.user,
                                         phone='test',
                                         city='test', 
                                         description='Test')
        profile.photo = self.photos[0]
        profile.photo.name = get_basename(self.photos[0].name)
        profile.save()
        response = self.client.get(reverse('profile'))
        # but now it should be rendered
        self.assertContains(response, f'<img src="{photo_media_url}" alt="testuser" class="profile-photo">')
        profile.delete()

    # profile should be edittable even if it does not exist yet
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def test_profile_edit_no_profile(self):
        self.client.login(username='testuser', password='12345')
        # as always are these view and template found?
        response = self.client.get(reverse('profile_edit'))
        # although the profile instance does not exist the page should be rendered
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/profile_edit.html')
        response = self.client.post(reverse('profile_edit'), {'first_name' : 'test', 
                                                              'last_name' : 'test',
                                                              'phone' : 'test',
                                                              'city' : 'test', 
                                                              'description' : 'Test', 
                                                              'photo' : self.photos[0]})
        # we are supposed to be redirected to profile details
        self.assertRedirects(response, reverse('profile'))
        # user extra info should've been updated
        self.assertTrue(User.objects.filter(username='testuser', first_name='test', last_name='test').exists())
        user = User.objects.get(username='testuser')
        # the profile instance bound to our test user should exist now
        self.assertTrue(hasattr(user, 'profile'))
        self.assertTrue(Profile.objects.filter(user=user, phone='test', city='test', description='Test').exists())
        user.profile.delete()
    
    @override_settings(MEDIA_ROOT = tempfile.gettempdir())
    def test_profile_edit(self):
        self.client.login(username='testuser', password='12345')
        self.client.post(reverse('profile_edit'), {'first_name' : 'test', 
                                                   'last_name' : 'test',
                                                   'phone' : 'test',
                                                   'city' : 'test', 
                                                   'description' : 'Test', 
                                                   'photo' : self.photos[0]})
        response = self.client.post(reverse('profile_edit'), {'first_name' : 'Test', 
                                                              'last_name' : 'Test',
                                                              'phone' : 'Test',
                                                              'city' : 'Test', 
                                                              'description' : 'Test', 
                                                              'photo' : self.photos[1]})
        # we are supposed to be redirected to profile details again
        self.assertRedirects(response, reverse('profile'))
        user = User.objects.get(username='testuser')
        # profile should've been updated now
        self.assertTrue(Profile.objects.filter(user=user, phone='Test', city='Test', description='Test').exists())
        user.profile.delete()
