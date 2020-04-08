from django.test import TestCase, Client, override_settings
from django.conf import settings
from .models import User, Post, Group, Follow
import time


class TestUserPost(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah",
            email="connor.s@skynet.com",
            password="12345"
            )
        self.client.login(username='sarah', password='12345')

    def test_create_profile_after_registration(self):
        response = self.client.get("/sarah/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/haras/")
        self.assertNotEqual(response.status_code, 200)

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_create_new_post(self):
        self.client.post(
            "/new/",
            {'text': 'test_post'},
            follow=True
            )
        response = self.client.get("/")
        self.assertContains(response, 'test_post')

    def test_post_redirect(self):
        self.client.logout()
        response = self.client.get("/new/")
        self.assertRedirects(response, '/auth/login/?next=/new/')

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_post_availably_after_create(self):
        post = Post.objects.create(text='test_post_all', author=self.user)
        response = self.client.get("/")
        self.assertContains(response, 'test_post_all')
        response = self.client.get("/sarah/") 
        self.assertContains(response, 'test_post_all')
        response = self.client.get(f"/sarah/{post.id}/")
        self.assertContains(response, 'test_post_all')

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_post_edit_in_all_pages(self):
        self.client.post(
            '/new/',
            {'text': 'test post'},
            follow=True
            )
        post = Post.objects.get(author=self.user)
        self.client.post(
            f'/sarah/{post.id}/edit/',
            {'text': 'test post availably'},
            follow=True
            )
        response = self.client.get('/')
        self.assertContains(response, 'test post availably')
        response = self.client.get("/sarah/")
        self.assertContains(response, 'test post availably')
        response = self.client.get(f"/sarah/{post.id}/")
        self.assertContains(response, 'test post availably')

    def test_page_404(self):
        response = self.client.get("/haras/")
        self.assertEqual(response.status_code, 404)


class TestPostImage(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah",
            email="connor.s@skynet.com",
            password="12345"
            )
        self.client.login(username='sarah', password='12345')
        self.group = Group.objects.create(
            title='Test',
            slug='Test',
            description='test group'
            )
        self.client.post(
            '/new/',
            {'text': 'test post', 'group': self.group.id},
            follow=True
            )

    def test_image_in_post_page(self):
        post = Post.objects.get(author=self.user)
        with open('./tests/header91.jpg', 'rb') as fp:
            self.client.post(
                f'/sarah/{post.id}/edit/',
                {'text': 'fred', 'image': fp}
                )
        response = self.client.get(f"/sarah/{post.id}/")
        self.assertContains(response, '<img')
        self.assertContains(response, '.jpg')

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_image_in_all_page(self):
        post = Post.objects.get(author=self.user)
        with open('./tests/header91.jpg', 'rb') as fp:
            self.client.post(
                f'/sarah/{post.id}/edit/',
                {
                    'text': 'fred',
                    'image': fp,
                    'group': self.group.id
                    }
                )
        response = self.client.get('/')
        self.assertContains(response, 'class="card-img"')
        response = self.client.get('/sarah/')
        self.assertContains(response, 'class="card-img"')
        response = self.client.get(f'/group/{self.group.slug}')
        self.assertContains(response, 'class="card-img"')

    def test_upload_valid_image(self):
        post = Post.objects.get(author=self.user)
        with open('./tests/test.txt', 'rb') as fp:
            self.client.post(
                f'/sarah/{post.id}/edit/',
                {'text': 'fred', 'image': fp}
                )
        response = self.client.get(f"/sarah/{post.id}/")
        self.assertNotContains(response, '.txt')


class TestCache(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testing",
            email="connor.s@skynet.com",
            password="12345"
            )
        self.client.login(username='testing', password='12345')

    def test_cache_index(self):
        response = self.client.get("/")
        post = Post.objects.create(text='test_cache', author=self.user)
        response = self.client.get("/")
        self.assertNotContains(response, 'test_cache')
        time.sleep(20)
        response = self.client.get("/")
        self.assertContains(response, 'test_cache')


class TestProfileFollowAndComment(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testing2",
            email="connor.s@skynet.com",
            password="12345"
            )
        self.client.login(username='testing2', password='12345')
        self.author1 = User.objects.create_user(
            username="author1",
            email="test1@skynet.com",
            password="12345"
            )
        self.author2 = User.objects.create_user(
            username="author2",
            email="test2@skynet.com",
            password="12345"
            )

    def test_authuser_follow_and_unfollow(self):
        user = User.objects.get(username=self.user.username)
        author = User.objects.get(username=self.author1.username)
        unfollow_author = User.objects.get(username=self.author2.username)
        follow_object = Follow.objects.create(user=user, author=author)
        status_follow = Follow.objects.filter(user=user, author=author)
        self.assertTrue(status_follow)
        status_follow = Follow.objects.filter(user=user, author=unfollow_author)
        self.assertFalse(status_follow)

    def test_new_post_in_follow_page(self):
        user = User.objects.get(username=self.user.username)
        author = User.objects.get(username=self.author1.username)
        follow_object = Follow.objects.create(user=user, author=author)
        post = Post.objects.create(text='test_post', author=author)
        response = self.client.get('/follow/')
        self.assertContains(response, 'test_post')

    def test_auth_unauth_comment_post(self):
        user = User.objects.get(username=self.user.username)
        post = Post.objects.create(text='test_post', author=user)
        self.client.post(
            f'/testing2/{post.id}/',
            {'text': 'comment'},
            follow=True
            )
        response = self.client.get(f'/testing2/{post.id}/')
        self.assertContains(response, 'comment')
