# The LadKrapht Server Infrastructure

### Dynamically deploys a Tekxit 3.14π server and automatically spins down and backs up the world


## How to use
- Create a file called `.env` and add your Discord bot token to it as `DISCORD_TOKEN`
- Create a key pair on AWS and name it `ladkrapht-login`, and put it in this directory as `ladkrapht-login.pem`
- Install Python requirements with `pip3 install -r requirements.txt`
- Fire up the Discord bot with `python3 kraphtbot.py` and run the `.start` commmand
- The bot will report its progress as it downloads server files and requirements, and will report the server IP in the chat when it is ready
- The IP address changes each time the server deploys
- The server will automatically shut down after 10 mins with no players online to save resources and back up the world files as `backup.zip`
- You can run server commands from here while the server is running by using the command script: `./cmd "say Hello World"`
