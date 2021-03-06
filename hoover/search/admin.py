from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import User, Group, UserAdmin, GroupAdmin
from django.forms import ModelForm
from . import models


class HooverAdminSite(admin.AdminSite):

    pass


class CollectionAdmin(admin.ModelAdmin):

    list_display = ['__str__', 'count', 'user_access_list', 'group_access_list', 'public']
    fields = ['title', 'name', 'index', 'public', 'users', 'groups']
    filter_horizontal = ['users', 'groups']

    def get_prepopulated_fields(self, request, obj=None):
        return {} if obj else {'name': ['title'], 'index': ['name']}

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == 'users':
            field.label_from_instance = self.get_user_label
        return field

    def get_user_label(self, user):
        name = user.get_full_name()
        username = user.username
        if name and name != username:
            return "{} ({})".format(username, name)
        else:
            return username


class GroupAdminForm(ModelForm):
    class Meta:
        model = Group
        exclude = []

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('users', False)
    )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        instance = super(GroupAdminForm, self).save()
        self.save_m2m()
        return instance


class HooverGroupAdmin(GroupAdmin):
    form = GroupAdminForm
    fields = ['name', 'users']
    exclude = ['permissions']


class HooverUserAdmin(UserAdmin):
    actions = []
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


admin_site = HooverAdminSite(name='hoover-admin')
admin_site.register(models.Collection, CollectionAdmin)
admin_site.register(Group, HooverGroupAdmin)
admin_site.register(User, HooverUserAdmin)
