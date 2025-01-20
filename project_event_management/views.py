from django.shortcuts import redirect, render

def HomePage(request):
    if request.user.is_authenticated and hasattr(request.user, 'organizer'):
        organizer_type = request.user.organizer.organizer_type
        if not organizer_type:  # Redirect if type is missing
            return redirect('update_profile')  # Replace with your update profile URL
    else:
        organizer_type = None

    context = {
        'organizer_type': organizer_type
    }
    return render(request, 'core/navbar.html', context)
