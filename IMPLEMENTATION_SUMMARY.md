# Dodonation Implementation Summary

## Current Status

The backend is implemented and the frontend is now connected for the main user flows:

- Donor registration, OTP verification, login
- NGO registration, OTP verification, login
- Donor profile and NGO profile viewing/updating
- Donor donation creation and donation listing
- NGO donation browsing and claim submission
- Donor claim review with accept/reject
- Google Meet scheduling from accepted claims
- Online meeting completion, location pinning, and physical handoff completion
- NGO permit upload and permit status viewing
- Authenticated chatbot access

This is a much more complete state than before. The project is no longer just "backend-ready"; the Flet app now has screens wired to the existing backend services for the core flows above.

---

## Backend Work Completed

### Authentication and OTP

- Separate donor and NGO registration endpoints
- Registration now includes a dedicated `username` field
- OTP generation and verification using the `OTPCode` model
- Request-new-OTP endpoint
- Login now accepts either username or email
- Login now returns clearer invalid-login messages for missing users vs incorrect passwords
- Custom login endpoint now returns both JWT tokens and serialized user data so the Flet app can route by role after login
- Current-user endpoint for authenticated profile lookup
- Inactive NGOs no longer receive a usable authenticated session immediately after OTP verification
  - OTP verification for inactive NGO accounts now returns a pending-approval response instead

### Profiles and Permits

- Donor and NGO profile endpoints for retrieving and updating the logged-in user's profile
- NGO permit upload endpoint
- NGO permit listing endpoint
- Admin permit approval/rejection endpoint
- NGO approval activates the NGO account
- NGO permit submission is now part of NGO registration
- NGO accounts now follow the intended approval flow:
  - register
  - upload permit during registration
  - verify OTP
  - wait for admin approval
  - log in after approval

### Donations, Claims, and Meetings

- Expanded `Donation` model with category, quantity, expiry, image, location, and status
- Added `ClaimRequest` workflow
- Added `Meeting` workflow tied to accepted claims
- Donor can now schedule a Google Meet only after accepting a claim
- Added staged meeting workflow:
  - `online_scheduled`
  - `online_completed`
  - `location_pinned`
  - `physical_completed`
- Added meeting location fields and workflow timestamps
- Completing the physical handoff clears the pinned map location and marks the donation as completed
- Added backend filtering support used by the mobile app:
  - Donations can be filtered by `category`, `status`, and `donor=me`
  - Claims can be filtered by `type=received` and `type=sent`
  - Meetings can be filtered by `status`

### Admin Improvements

- Better dropdown labels via clearer model `__str__` methods
- Profile dropdowns restricted to the correct user roles
- Meeting admin only offers accepted claims
- Admin dropdowns are no longer effectively blank

---

## Frontend Work Completed

### Connected Screens

The Flet app now includes and routes to:

- `/` - Login
- `/role-selection` - Registration role selection
- `/register/donor` - Donor registration
- `/register/ngo` - NGO registration
- `/otp` - OTP verification
- `/dashboard` - Role-aware dashboard
- `/profile` - Donor/NGO profile screen
- `/donations` - Donation creation/listing and NGO claiming
- `/claims` - Claim review and response
- `/meetings` - Google Meet scheduling and staged meeting workflow
- `/permits` - NGO permit upload and status
- `/chatbot` - Authenticated chatbot
- `/map` - Meeting location editor

### Service Layer Integration

The frontend is now wired to the backend for:

- Auth
- Profiles
- Donations
- Claims
- Meetings
- Permits
- Chatbot

### UX / Flow Fixes

- OTP screen now pre-fills the email from the registration flow
- OTP screen now keeps the registered email locked in place
- Dashboard now exposes the actual working app sections instead of only chatbot/map
- Meeting flow now matches the donor-led handoff process:
  - donor accepts claim
  - donor schedules Google Meet
  - donor marks online meeting complete
  - donor pins physical meeting point
  - NGO sees the pinned-location status in-app
  - donor marks physical handoff complete
- Meeting location saving is connected to the dedicated location pinning endpoint
- Donation image upload now uses multipart requests correctly when an image path is provided
- Donation image selection now uses a native file picker instead of a manual image-path field
- NGO permit selection now uses a native file picker instead of a manual file-path field
- Dashboard now shows username instead of email in the main welcome card
- Claims UI now better reflects donor vs NGO usage
- Several desktop Flet screens were restyled for a more consistent layout, card structure, and back navigation

---

## Files Added or Updated in This Pass

### Backend

- `backend/accounts/views.py`
- `backend/accounts/serializers.py`
- `backend/accounts/urls.py`
- `backend/donations/views.py`
- `backend/meetings/views.py`
- `backend/meetings/models.py`
- `backend/meetings/serializers.py`
- `backend/meetings/google_meet.py` (new)
- `backend/meetings/migrations/0003_google_meet_workflow.py` (new)
- `backend/config/settings.py`
- `backend/requirements.txt`

### Frontend

- `mobile_app/main.py`
- `mobile_app/services/auth_service.py`
- `mobile_app/services/donation_service.py`
- `mobile_app/views/dashboard.py`
- `mobile_app/views/register.py`
- `mobile_app/views/otp.py`
- `mobile_app/views/map.py`
- `mobile_app/views/donations.py` (new)
- `mobile_app/views/claims.py` (new)
- `mobile_app/views/profile.py` (new)
- `mobile_app/views/permits.py` (new)
- `mobile_app/views/meetings.py` (new)
- `mobile_app/services/meeting_service.py`
- `mobile_app/services/profile_service.py`
- `mobile_app/services/permit_service.py`
- `mobile_app/utils/app_state.py` (new)
- `mobile_app/utils/helpers.py`

---

## What Still Needs Work

The project is much closer to complete, but a few things are still unfinished or should be improved:

### Product / Feature Gaps

- Better map pinning UI
  - The map screen now supports a Flet map layout, but the experience still needs polish and depends on the optional `flet-map` package
- NGO waiting/approval UX
  - The backend flow is now correct, but there is not yet a dedicated polished waiting screen after OTP verification for NGOs pending approval
- Donation editing/deletion UI
- Real push/in-app notification system
  - NGOs currently see pinned-location updates via meeting status in the app, but there is no background notification delivery yet
- Better donor/NGO dashboard navigation and role-specific polish
- Google Meet environment setup
  - the code now calls the Google Meet API, but the backend still needs valid Google credentials configured through `GOOGLE_APPLICATION_CREDENTIALS`

### Environment Risk

- SQLite under OneDrive is still a real issue in this project
- The app may hit intermittent `disk I/O error` again because the project and `db.sqlite3` are inside a OneDrive-synced directory
- Safest long-term fix:
  - move the project outside OneDrive before continuing heavy local development

---

## Is Backend and Frontend Connected?

Yes, for the main application flows.

The frontend is now connected to the backend for authentication, profiles, donations, claims, meetings, permits, and chatbot usage. It is no longer only partially wired.

What is still not fully polished is the user experience around map pinning, approval-state UX, and some secondary actions.

---

## Recommended Next Steps

1. Move the project out of OneDrive to avoid more SQLite write failures.
2. Run the backend with `python manage.py runserver`.
3. Run the Flet app with `python main.py`.
4. Configure Google Meet credentials for the backend and install the new backend dependencies.
5. Run `python manage.py migrate`.
6. Test this end-to-end flow:
   - Register donor
   - Verify donor OTP
   - Register NGO
   - Upload NGO permit during registration
   - Verify NGO OTP
   - Approve permit in admin
   - Log in as NGO after approval
   - Donor creates donation
   - NGO claims donation
   - Donor accepts claim
   - Donor schedules Google Meet
   - Donor marks online meeting complete
   - Donor pins meeting location
   - Donor marks physical handoff complete
7. After that, improve the interactive map picker and notification delivery.
