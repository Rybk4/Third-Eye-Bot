# Third-Eye-Bot

It is a Telegram bot written in Python, with built-in trained AI capable of recognizing objects in photos. It uses the ``telebot`` library for user interaction and the ``TensorFlow`` machine learning framework for image processing.

**Bot functions:**
- Receives images from users and identifies objects in them.
- Sends the name of the found objects to the user.
- Has a pre-training mechanism: users can add new objects or correct errors, improving the accuracy of the model.
- The trained data is stored, allowing the bot to get smarter over time.

A local project directory is used to store the data. The bot runs on a local server and can periodically retrain the model on new data.

