# web-project-1

Complete dynamic website based on a simulated [Client quote](documents/client_quote.md)

## Project management and design links

- [Trello board](https://trello.com/b/vrBD7pIS/web-project-1)
- [DB models and relationships](https://www.figma.com/board/e4y5DHNDaa0zgeNinXxJSD/App-models-scheme?node-id=0-1&t=i3NrjN3kfsYs7XeD-1)
- [Wireframes](https://www.figma.com/design/MqkhYF9iCc9kLxuaGuAJND/Picnic-App-wireframes?node-id=0-1&t=ZuXvo7s0QD0UlMwA-1)
- [Design System](documents/design_system.pdf)

## Project purpose

The purpose of this project is to develop a dynamic web application that provides a simple way to organize and participate in picnics.

## Client need

Picnic Planner is a collaborative web application designed to simplify the organization of group picnics and outdoor gatherings. Organizers often rely on group chats to coordinate supplies, which can lead to duplicate items and forgotten essentials. The application should provide a shared planning space where organizers and guests can collaborate, assign responsibilities, and keep all picnic information in one place.

An organizer creates a picnic and shares an invitation code with guests. Participants can add items under categories such as food, drinks, equipment, and entertainment. Guests can claim items they plan to bring, release them if their plans change, and see the responsibilities of other participants. Important unclaimed items are highlighted so that essential supplies are not forgotten.

## Main features

### User accounts

- User registration.
- User login and logout.
- Password hashing.
- Organizer-specific picnic management.

### Picnic management

- Create a picnic.
- Add picnic name, date, location, and categories.
- Edit picnic details.
- Delete a picnic.
- View a list of picnics belonging to the logged-in organizer.

### Guest participation

- Join a picnic without creating a registered account.
- Join using the picnic name and invitation code.
- Generate a unique guest PIN for returning guests.
- Return to a picnic using the invitation code and the guest PIN.
- Display the active guest as "you" where appropriate.

### Item management

- Add items to a picnic in a specific category.
- Claim (grab) an available item.
- Unclaim (drop) an item.
- Display the user or guest responsible for a claimed item.
- Prevent inappropriate deletion of claimed items.
- Allow both registered users and guests to participate in item management where permitted.
- Edit items where permitted (if not claimed or claimed by current user/guest) and reassign category.

### User interface

- Responsive layouts for different screen sizes.
- Separate organizer and guest picnic views.
- Guest joining interface with tabs for first-time and returning guests.
- Picnic overview interface with tabs for details and participants.
- Styled forms and buttons.
- Flash messages for successful and unsuccessful actions.
- JavaScript functionality to close flash messages.
- JavaScript confirmation popup to prevent accidental picnic deletion.
- JavaScript copy-to-clipboard functionality for picnic information, with success and error feedback.
- Dynamic category illustrations based on the selected item category.
- Progressive enhancement using JavaScript without replacing the existing Flask/Jinja functionality.

## Project structure

The project follows a Flask application structure with templates for the different pages, four Blueprints that organize routes by purpose, and static files for CSS, JavaScript, and images.

```text
web-project-1/
│
├── documents/
│ ├── journal/
│ ├── client_quote.md
│ └── design_system.pdf
│
├── instance/
│ └── ...
│
├── routes/
│ ├── guest.py
│ ├── item.py
│ ├── picnic.py
│ └── user.py
│
├── static/
│ ├── css/
│ │ └── style.css
│ ├── images/
│ │ └── ...
│ └── js/
│ └── app.js
│
├── templates/
│ ├── base.html
│ ├── create_picnic.html
│ ├── edit_item.html
│ ├── edit_picnic.html
│ ├── index.html
│ ├── join_picnic.html
│ ├── login.html
│ ├── picnic.html
│ ├── picnics.html
│ └── register.html
│
├── .env
├── .gitignore
├── app.py
├── models.py
└── README.md
```

## Technology choices

### Backend

- Python
- Flask – web application framework.
- Flask-SQLAlchemy – database integration and ORM.
- Flask-Login – user authentication and session management.
- Jinja – server-side HTML templating.
- SQLite – development database.

### Frontend

- HTML5 – page structure.
- CSS – layout, styling, and responsive design.
- JavaScript – interactive features and progressive enhancement.

### Design and project management

- Figma – wireframes and interface design.
- FigJam – database/model relationship planning.
- Trello – project planning and task management.
- Git/GitHub – version control and repository management.

## Endpoints

1. home
2. registration page
3. login page
4. guest join picnic page
5. returning guest join picnic page
6. overview page for organizer (registered user) with create picnic button and picnics list
7. add picnic form page
8. edit picnic form page
9. picnic overview page for organizer
10. picnic overview page for guests
11. add items form
12. claim / unclaim item functionality
13. edit / delete item functionality
14. delete picnic
