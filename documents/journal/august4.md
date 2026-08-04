1. What did I complete?

Today I attended class and followed a step-by-step demonstration on frontend and backend integration. It gave me a much clearer understanding of how to organize my project. After class, I created the project folder structure and the main files.

I then set up the development environment by creating a Python virtual environment and installing the required dependencies, including Flask, Flask-Dotenv, SQLAlchemy, and Flask-Login. I created the static folder for JavaScript and CSS files and the templates folder for the HTML templates. After initializing the application, I successfully tested that it was running by displaying the Welcome message from the index.html template.

Next, I implemented the User and Picnic models. I decided to store item categories as strings because the available categories are fixed and users will choose them from predefined checkboxes. While designing the database, I realized that I also needed an Item model. Each item will belong to a picnic, have a category label for display purposes, and contain information about whether it has been claimed.

2. What am I working on next?

Tomorrow I plan to finish implementing the Item model, define its relationships, and continue building the database structure. I also want to continue researching the best way to implement item claiming.

3. What is blocking me?

I am currently unsure how to design the claiming mechanism for items. Items need to support the grab and drop methods, update their claimed status, and display who claimed them. However, since both registered users and guests can claim items, I am not sure how to associate the user/guest with an item. Using user id is not sufficient because guests are stored separately and their IDs may overlap with user IDs. I plan to discuss this design decision with the instructor.
