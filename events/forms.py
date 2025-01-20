from django import forms
from .models import (
    FoodAndBeveragePost, ConversationHallPost, FunAndActivitiesPost,
    FoodCategory, ConversationHallCategory, FunAndActivitiesCategory
)

class FoodAndBeveragePostForm(forms.ModelForm):
    food_category = forms.ModelChoiceField(queryset=FoodCategory.objects.all(), empty_label="Select Food Category")

    class Meta:
        model = FoodAndBeveragePost
        fields = ['title', 'description', 'food_category', 'image', 'price', 'quantity']


class ConversationHallPostForm(forms.ModelForm):
    hall_category = forms.ModelChoiceField(queryset=ConversationHallCategory.objects.all(), empty_label="Select Hall Category")

    class Meta:
        model = ConversationHallPost
        fields = ['title', 'description', 'hall_category', 'image', 'price']


class FunAndActivitiesPostForm(forms.ModelForm):
    activity_category = forms.ModelChoiceField(queryset=FunAndActivitiesCategory.objects.all(), empty_label="Select Activity Category")

    class Meta:
        model = FunAndActivitiesPost
        fields = ['title', 'description', 'activity_category', 'image', 'price']
