from django.test import TestCase
from django.urls import reverse
from catalog.models import Author, Book, BookInstance, Genre
import datetime

class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Configuración inicial para TODAS las pruebas de la clase
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('last_name').verbose_name
        self.assertEqual(field_label, 'last name')

    def test_date_of_birth_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEqual(field_label, 'date of birth')

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'died')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)

    def test_last_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('last_name').max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f'{author.last_name}, {author.first_name}'
        self.assertEqual(str(author), expected_object_name)

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        self.assertEqual(author.get_absolute_url(), '/catalog/author/1')

class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crear un autor para el libro
        test_author = Author.objects.create(first_name='John', last_name='Doe')
        # Crear un libro
        Book.objects.create(
            title='Test Book Title',
            summary='Test book summary',
            isbn='1234567890123',
            author=test_author
        )

    def test_title_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_title_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_get_absolute_url(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book.get_absolute_url(), '/catalog/book/1')

class BookInstanceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crear datos de prueba para BookInstance
        test_author = Author.objects.create(first_name='John', last_name='Doe')
        test_book = Book.objects.create(
            title='Test Book',
            summary='Test summary',
            isbn='1234567890123',
            author=test_author
        )
        # Crear una instancia de libro y GUARDARLA COMO ATRIBUTO
        cls.book_instance = BookInstance.objects.create(
            book=test_book,
            imprint='Test Imprint',
            due_back=datetime.date.today() + datetime.timedelta(weeks=2)
        )

    def test_is_overdue_property(self):
        # Usar self.book_instance en lugar de buscar por ID
        book_instance = self.book_instance
        
        # Probar cuando no está vencido
        self.assertFalse(book_instance.is_overdue)
        
        # Probar cuando está vencido
        book_instance.due_back = datetime.date.today() - datetime.timedelta(days=1)
        book_instance.save()
        self.assertTrue(book_instance.is_overdue)

    def test_string_representation(self):
        book_instance = self.book_instance
        self.assertIn('Test Book', str(book_instance))