"""Test module for imager profile app."""

from django.test import TestCase

import factory

from imager_images.models import Album, Photo

from imager_profile.models import ImagerProfile, User


class PhotoFactory(factory.django.DjangoModelFactory):
    """Photo factory to make photos."""

    class Meta:
        """Meta class."""

        model = Photo

    title = factory.Sequence(lambda n: f'Photo{n}')


class PhotoTestCase(TestCase):
    """Photo test case."""

    # @classmethod
    # def setUpClass(cls):

    def setUp(self):
        """Setup."""
        jimbo = User(username='Jimbo',
                     password='p@ssw0rd')
        jimbo.save()
        j_profile = jimbo.profile
        j_profile.location = "Buffalo"
        j_profile.save()
        album = Album(user=j_profile, title='The Album')
        album.save()
        for i in range(30):
            photo = PhotoFactory.build()
            photo.user = j_profile
            # photo = Photo(user=j_profile, title=f'Pic{i}')
            photo.save()
            album.photos.add(photo)
        self.album = album


    def test_user_has_30_photos(self):
        """Test that user Jimbo has 30 photo."""
        one_user = User.objects.first()
        self.assertEqual(one_user.profile.photo_set.count(), 30)


    def test_first_photo_title_startswith_Photo(self):
        """Test that user Jimbo has 30 photo."""
        one_user = User.objects.first()
        pic = one_user.profile.photo_set.first()
        self.assertTrue(pic.title.startswith('Photo'))


    def test_album_created(self):
        """Test that the album is created."""
        one_album = Album.objects.get()
        self.assertIsNotNone(one_album)


    def test_album_title_is_the_album(self):
        """Test that the album title is The Album."""
        one_album = Album.objects.get()
        self.assertEqual(one_album.title, 'The Album')


    def test_album_has_photos(self):
        """."""
        self.assertTrue(self.album.photos.count() == 30)

    def test_photo_with_album_points_to_album(self):
        """."""
        a_photo = Photo.objects.order_by('?').first()
        self.assertTrue(self.album in a_photo.albums.all())
