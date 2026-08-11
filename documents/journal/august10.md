1. What did I complete?

Today I planned my work for the week and finished the remaining backend functionality from the previous week.

I continued working on the backend of my Picnic App, focusing mainly on allowing both registered organizers and guests to interact with picnic items. I updated the guest access workflow by using the Flask session to store the guest ID after a guest joins a picnic or returns using their invitation code and PIN. This allows the application to identify the guest across different requests without requiring them to create an account or log in.

I modified the picnic access logic so that the same picnic page can now be accessed by either the organizer or a valid guest. I also updated the item functionality so that both organizers and guests can add and claim items. For dropping items, I added validation to ensure that only the participant who claimed an item can drop it.

I then implemented item editing and deletion. Both organizers and guests can edit unclaimed items or items they have personally claimed. Unclaimed items can also be deleted by any participant who has access to the picnic, while claimed items cannot be deleted.

Finally, I implemented the picnic edit and delete functionality for organizers. When editing a picnic, the organizer can update its details and selected categories. While working on the picnic deletion logic, I encountered the error `sqlalchemy.exc.IntegrityError: NOT NULL constraint failed: item.picnic_id`. The issue occurred because the items associated with the picnic could not have a null `picnic_id`. I resolved this by updating the Picnic model relationships to use cascade deletion. Now, when a picnic is deleted, its related items and guests are deleted automatically as well.

2. What am I working on next?

Next, I will start working on this week's frontend implementation. I plan to gradually replace the current Flask/Jinja-based display and form interactions with JavaScript and fetch, connecting the frontend to Flask endpoints and rendering the picnic data dynamically.
