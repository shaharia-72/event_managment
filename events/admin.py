from django.contrib import admin
from .models import (
    Organization, AdminApprovalRequest, FoodCategory, ConversationHallCategory,
    FunAndActivitiesCategory, FoodAndBeveragePost, ConversationHallPost, FunAndActivitiesPost
)

# Inline model admin classes for posts if needed
class FoodAndBeveragePostInline(admin.TabularInline):
    model = FoodAndBeveragePost
    extra = 1  # The number of empty forms to display by default
    ordering = ['title']  # Optionally define the ordering

class ConversationHallPostInline(admin.TabularInline):
    model = ConversationHallPost
    extra = 1
    ordering = ['title']

class FunAndActivitiesPostInline(admin.TabularInline):
    model = FunAndActivitiesPost
    extra = 1
    ordering = ['title']


# Organization admin
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('organizer', 'is_active_food_and_beverage', 'is_active_conversation_hall', 'is_active_fun_and_activities')
    list_filter = ('is_active_food_and_beverage', 'is_active_conversation_hall', 'is_active_fun_and_activities')
    search_fields = ('organizer__name',)  # Assuming the Organizer model has a name field
    inlines = [FoodAndBeveragePostInline, ConversationHallPostInline, FunAndActivitiesPostInline]


# AdminApprovalRequest admin
@admin.register(AdminApprovalRequest)
class AdminApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ('organization', 'tag', 'status', 'updated_at')  # Updated 'is_approved' to 'status'
    list_filter = ('status', 'tag', 'created_at')  # Updated 'is_approved' to 'status'
    search_fields = ('organization__name', 'tag', 'status')
    ordering = ('-updated_at',)


# Category admin (Food, Conversation Hall, and Fun & Activities)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)

class FoodCategoryAdmin(CategoryAdmin):
    pass

class ConversationHallCategoryAdmin(CategoryAdmin):
    pass

class FunAndActivitiesCategoryAdmin(CategoryAdmin):
    pass


# Post admin (Food, Conversation Hall, and Fun & Activities)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'price', 'quantity', 'image')
    search_fields = ('title', 'organization__name')
    list_filter = ('organization',)

class FoodAndBeveragePostAdmin(PostAdmin):
    list_display = ('title', 'organization', 'food_category', 'price', 'quantity')

class ConversationHallPostAdmin(PostAdmin):
    list_display = ('title', 'organization', 'hall_category', 'price')

class FunAndActivitiesPostAdmin(PostAdmin):
    list_display = ('title', 'organization', 'activity_category', 'price')


# Register models in admin (Remove the second registration of AdminApprovalRequest)
admin.site.register(Organization, OrganizationAdmin)
# admin.site.register(AdminApprovalRequest, AdminApprovalRequestAdmin)  # Remove this line
admin.site.register(FoodCategory, FoodCategoryAdmin)
admin.site.register(ConversationHallCategory, ConversationHallCategoryAdmin)
admin.site.register(FunAndActivitiesCategory, FunAndActivitiesCategoryAdmin)
admin.site.register(FoodAndBeveragePost, FoodAndBeveragePostAdmin)
admin.site.register(ConversationHallPost, ConversationHallPostAdmin)
admin.site.register(FunAndActivitiesPost, FunAndActivitiesPostAdmin)
