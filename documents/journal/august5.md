1. What did I complete?

Today, I discussed with the instructor the possible ways to assign items to both registered users and guests. We decided to handle item claiming according to the claimant type.

Using this approach, I completed the `Item` model and created the `Guest` model. I added relationships between users, guests, and items so that both registered users and guests can store a list of the items they have claimed. Each item can store either a `claimed_by_user_id` or a `claimed_by_guest_id`, depending on who claimed it, or neither if the item has not yet been claimed.

I also completed the user registration, login, and logout logic and tested that each workflow functions correctly.

After that, I started developing the picnic overview and picnic creation pages. At this stage, I added only the essential functionality needed to test whether the database tables are created correctly and whether data can be saved and retrieved.

For this initial backend stage, I used Flask routes to process data, Jinja templates to display it, and flash messages to show validation errors and success messages. I plan to replace some of this functionality with JavaScript and `fetch()` later as the frontend becomes more developed.

2. What am I working on next?

Tomorrow, I will demonstrate the minimum working flow for Deliverable 2:

Register a new user → log in → create a picnic → view the user’s picnics → log out.

After completing this demonstration, my next step will be to add a route for viewing the details of a single picnic. I will then test adding items to a picnic and claiming or dropping them.

I also plan to implement the guest workflow, including joining a picnic and testing whether a guest can successfully claim an item.

3. What is blocking me?

There are no specific technical blockers at the moment. However, the amount of remaining work is significant, so I may need to reduce the project scope and prioritize the essential features first.
