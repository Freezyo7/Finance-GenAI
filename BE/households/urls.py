from django.urls import path
from .views import (
    HouseholdListCreateView,
    HouseholdDetailView,
    HouseholdMemberListView,
    HouseholdMemberDetailView,
    HouseholdInvitationListCreateView,
    AcceptInvitationView,
)

urlpatterns = [
    path("",HouseholdListCreateView.as_view(), name="household-list-create"),
    path("<uuid:pk>/", HouseholdDetailView.as_view(), name="household-detail"),

    path("<uuid:household_id>/members/", HouseholdMemberListView.as_view(), name="household-member"),
    path("<uuid:household_id>/members/<uuid:member_id>/", HouseholdMemberDetailView.as_view(), name="househol-member-detail"),

    path("<uuid:household_id>/invitations/", HouseholdInvitationListCreateView.as_view(), name = "household-invitations"),
    path("invitations/accept/", AcceptInvitationView.as_view(), name = "household-invitation-accept"),
]