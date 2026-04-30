Team members:
-  Tanyah Elaheebux (2413945)
-  Yogendra Mukteshwur Nundlall (2413100)
-  Krishna Rungasamy (2413950)
-  Poshita Beersee (2413580)
-  Gouruchana Devi Maghoo (2413925)

For the Dodonation mobile app:
1.User Roles:
Donor:
- View donation posts
- Track donation status (available, pending, claimed, rejected)
- Schedule meetings with NGOs
- Pin physical meeting location
NGO:
- Register and submit permit for approval
- Access app only after admin validation
- Get an email after their account has been activated
- Claim donations
- Coordinate meetings with donors
- leave a rating
Admin:
- Approve ngo permits and activate their accounts
- can activate, suspend or delete any accounts
- can accept claim request and schedule meetings
- can create new users

2.Authentication Flow:
- Register as Donor or NGO
- Verify OTP
NGO users:
- Must wait for admin approval
- Will see pending message until approved

3.Meeting Workflow:

The app follows a strict meeting lifecycle:

online_scheduled 
→ online_completed 
→ location_pinned (using flet map)
→ physical_completed
→ NGO provides ratings about donor
Actions:
Complete Online Meeting
Pin Physical Location
Complete Physical Meeting
Submit rating

Each step is only enabled when the previous one is completed.

Meeting Flow:
Step 1: Schedule Meeting
Donor provides Google Meet link
A small counter indicating number of minutes remaining before online meeting (it disappears after online meeting is completed)
Step 2: Complete Online Meeting

Changes status:
online_scheduled → online_completed
Step 3: Pin Physical Location
Navigate to Map Screen
Select location
Click Save Location

Changes status:
online_completed → location_pinned
Step 4: Complete Physical Meeting
Final confirmation
The ngo can upload proof of receiving the donations after physical meeting (upload by using phone camera/ upload if running the app on a PC)

Status:
location_pinned → physical_completed → NGO leaves a rating about the donor
