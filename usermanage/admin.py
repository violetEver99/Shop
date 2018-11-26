from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from usermanage.models import UserProfile

# Define an inline admin descriptor for UserProfile model
# which acts a bit like a singleton
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from usermanage.models import GroupProfile

# Define an inline admin descriptor for GroupProfile model
# which acts a bit like a singleton
class GroupProfileInline(admin.StackedInline):
    model = GroupProfile
    can_delete = False
    verbose_name_plural = 'profile'

# Define a new Group admin
class GroupAdmin(GroupAdmin):
    inlines = (GroupProfileInline, )

# Re-register GroupAdmin
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)