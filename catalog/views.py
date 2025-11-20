from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from django.contrib.auth.decorators import login_required, permission_required
from .models import Book, Author, BookInstance, Genre
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import RenewBookForm
from .forms import RenewBookModelForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin


def index(request):
    """
    Función vista para la página inicio del sitio.
    """
    # Genera contadores de algunos de los objetos principales
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    # Libros disponibles (status = 'a')
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # El 'all()' esta implícito por defecto.
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    # Renderiza la plantilla HTML index.html con los datos en la variable contexto
    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors, 'num_visits': num_visits,},
    )
class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Vista para listar libros prestados al usuario actual."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(
            borrower=self.request.user
        ).filter(
            status__exact='o'
        ).order_by('due_back')
    

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # Si es POST request, procesar datos del formulario
    if request.method == 'POST':
        # Crear instancia del formulario y poblar con datos del request
        form = RenewBookForm(request.POST)  # Asegúrate de usar RenewBookForm
        
        if form.is_valid():
            # Procesar los datos en form.cleaned_data
            book_instance.due_back = form.cleaned_data['renewal_date']  # Usar 'renewal_date'
            book_instance.save()
            return HttpResponseRedirect(reverse('all-borrowed'))
    
    # Si es GET (o cualquier otro método) crear formulario por defecto
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})  # Usar 'renewal_date'

    context = {
        'form': form,
        'book_instance': book_instance,
    }
    
    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

# VISTA PARA DETALLE DE AUTOR (FALTANTE)  
class AuthorDetailView(generic.DetailView):
    model = Author

# VISTA PARA TODOS LOS LIBROS PRESTADOS (FALTANTE)
class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
    

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2023'}  # Fecha de ejemplo
    permission_required = 'catalog.add_author'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__'  # No recomendado para producción
    permission_required = 'catalog.change_author'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'