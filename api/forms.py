from django import forms
from .models import Book

class BookSelectionForm(forms.Form):
    selected_book = forms.ChoiceField(
        label="Select a Book",
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[("", "Choose a book")]  # Add an initial empty choice
    )
    question_query = forms.CharField(
        label="Ask your question",
        max_length=1000,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        user_books = kwargs.pop('user_books', None)
        super(BookSelectionForm, self).__init__(*args, **kwargs)

        # Populate choices for selected_book field with user's books
        if user_books:
            book_choices = [(book.id, f"{book.book_name} - {book.book_category}") for book in user_books]
            self.fields['selected_book'].choices += book_choices
