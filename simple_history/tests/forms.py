from django import forms

from simple_history.forms import ReadOnlyFieldsMixin, new_readonly_form_class

from .models import Poll


class PollRevertForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = '__all__'


class ReadOnlyPollRevertForm(ReadOnlyFieldsMixin, PollRevertForm):
    all_fields = True



GeneratedByFunctionReadOnlyPollRevertForm = new_readonly_form_class(PollRevertForm, readonly_fields=())
