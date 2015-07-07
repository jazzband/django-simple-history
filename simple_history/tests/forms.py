from django import forms

from simple_history.forms import ReadOnlyFieldsMixin, new_readonly_form

from .models import Poll


class PollRevertForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = '__all__'


class ReadOnlyPollRevertForm(ReadOnlyFieldsMixin, PollRevertForm):
    pass


GeneratedByFunctionReadOnlyPollRevertForm = new_readonly_form(PollRevertForm, readonly_fields=())
