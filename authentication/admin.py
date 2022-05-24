from django.contrib import admin

from .models import *

# Register your models here.
# admin of cash app
admin.site.register(Currency)
admin.site.register(Bank)
admin.site.register(Wallet)
admin.site.register(Transaction)

# admin of user
admin.site.register(UserInformation)

# admin of profile
admin.site.register(Profile)

admin.site.register(Contacts)
admin.site.register(BankCard)
# admin.site.register(BankName)
admin.site.register(Inflow)
admin.site.register(Category)
admin.site.register(Outflow)
