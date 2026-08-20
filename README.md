# web-project-1

Complete dynamic website based on a simulated [Client quote](documents/client_quote.md)

## Project management and design links

- [Trello board](https://trello.com/b/vrBD7pIS/web-project-1)
- [DB models and relationships](https://www.figma.com/board/e4y5DHNDaa0zgeNinXxJSD/App-models-scheme?node-id=0-1&t=i3NrjN3kfsYs7XeD-1)
- [Wireframes](https://www.figma.com/design/MqkhYF9iCc9kLxuaGuAJND/Picnic-App-wireframes?node-id=0-1&t=ZuXvo7s0QD0UlMwA-1)

## Client need

Picnic Planner is a collaborative web application designed to simplify the organization of group picnics and outdoor gatherings. Organizers often rely on group chats to coordinate supplies, which can lead to duplicate items and forgotten essentials. The application should provide a shared planning space where organizers and guests can collaborate, assign responsibilities, and keep all picnic information in one place.

An organizer creates a picnic and shares an invitation code with guests. Participants can add items under categories such as food, drinks, equipment, and entertainment. Guests can claim items they plan to bring, release them if their plans change, and see the responsibilities of other participants. Important unclaimed items are highlighted so that essential supplies are not forgotten.

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
