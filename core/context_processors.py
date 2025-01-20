from events.models import AdminApprovalRequest

def organizer_approval_status(request):
    """
    Add approval statuses for organizer features to the context.
    """
    if request.user.is_authenticated and hasattr(request.user, 'organizer'):
        try:
            organization = request.user.organizer.organization

            # Fetch the approval statuses
            food_approval_status = get_approval_status(organization, 'food_and_beverage')
            hall_approval_status = get_approval_status(organization, 'conversation_hall')
            activity_approval_status = get_approval_status(organization, 'fun_and_activities')

            return {
                'food_approval_status': food_approval_status,
                'hall_approval_status': hall_approval_status,
                'activity_approval_status': activity_approval_status,
            }
        except AttributeError:
            pass  # User does not have an associated organization
    return {}

def get_approval_status(organization, tag):
    """
    Helper function to get the approval status for a feature (food, hall, or activity).
    """
    approval_request = AdminApprovalRequest.objects.filter(organization=organization, tag=tag).first()
    if approval_request:
        if approval_request.is_approved:
            return 'Approved'
        return 'Pending'
    return 'Not Requested'
