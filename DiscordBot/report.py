from enum import Enum, auto
import discord
import re

class State(Enum):
    REPORT_START = auto()
    AWAITING_MESSAGE = auto()
    MESSAGE_IDENTIFIED = auto()
    CLASSIFY_MESSAGE = auto()
    CLASSIFY_HATEFUL = auto()
    CLASSIFY_SEXUAL = auto()
    CLASSIFY_VIOLENT = auto()
    CLASSIFY_SPAM = auto()
    REPORT_DIRECTED_TO = auto()
    REPORT_COMPLETE = auto()

class Report:
    START_KEYWORD = "report"
    CANCEL_KEYWORD = "cancel"
    HELP_KEYWORD = "help"
    HATEFUL_KEYWORDS = ["doxxing", "bullying", "hate speech"]
    SEXUAL_KEYWORDS = ["nonconsensual", "unwanted", "child"]
    VIOLENT_KEYWORDS = ["self harm", "glorifying violence"]
    SPAM_KEYWORDS = ["spam", "impersonation"]

    def __init__(self, client):
        self.state = State.REPORT_START
        self.client = client
        self.reporter = None 
        self.message = None
        self.report_category = None
        self.block = None 
        self.report_subcategory = None
        self.directed_to = None 

    async def handle_message(self, message):
        '''
        This function makes up the meat of the user-side reporting flow. It defines how we transition between states and what 
        prompts to offer at each of those states. You're welcome to change anything you want; this skeleton is just here to
        get you started and give you a model for working with Discord. 
        '''
        content = message.content.lower()
        self.reporter = message.author

        if content == self.CANCEL_KEYWORD:
            self.state = State.REPORT_COMPLETE
            return ["Report cancelled."]
        
        if self.state == State.REPORT_START:
            reply =  "Thank you for starting the reporting process. " 
            reply += "Say `help` at any time for more information.\n\n"
            reply += "Please copy paste the link to the message you want to report.\n"
            reply += "You can obtain this link by right-clicking the message and clicking `Copy Message Link`."
            self.state = State.AWAITING_MESSAGE
            return [reply]
        
        if self.state == State.AWAITING_MESSAGE:
            # Parse out the three ID strings from the message link
            m = re.search('/(\d+)/(\d+)/(\d+)', message.content)
            if not m:
                return ["I'm sorry, I couldn't read that link. Please try again or say `cancel` to cancel."]
            guild = self.client.get_guild(int(m.group(1)))
            if not guild:
                return ["I cannot accept reports of messages from guilds that I'm not in. Please have the guild owner add me to the guild and try again."]
            channel = guild.get_channel(int(m.group(2)))
            if not channel:
                return ["It seems this channel was deleted or never existed. Please try again or say `cancel` to cancel."]
            try:
                message = await channel.fetch_message(int(m.group(3)))
            except discord.errors.NotFound:
                return ["It seems this message was deleted or never existed. Please try again or say `cancel` to cancel."]

            # Here we've found the message - it's up to you to decide what to do next!
            self.state = State.MESSAGE_IDENTIFIED
            self.message = message
            return ["I found this message:", "```" + message.author.name + ": " + message.content + "```", \
                    "Do you want to block the user? Please type y/n."]
        
        if self.state == State.MESSAGE_IDENTIFIED:
            if content == 'y': 
                reply = "If you wish to block the user who posted this message, follow these steps:\n"
                reply += "1. Right-click on the user's name in the chat.\n"
                reply += "2. Click `Block` in the dropdown menu.\n" 
                reply += "Could you tell us why you flagged this message?\n" 
                reply += "Please type `hateful content`, `sexual content`, `spam`, `violent content`."
                self.state = State.CLASSIFY_MESSAGE
                self.block = True 
                return [reply]
            elif content == 'n':
                reply = "Could you tell us why you flagged this message?\n" 
                reply += "Please type `hateful content`, `sexual content`, `spam`, `violent content`."
                self.state = State.CLASSIFY_MESSAGE
                self.block = False 
                return [reply]

        if self.state == State.CLASSIFY_MESSAGE:
            if "hateful content" in content:
                self.state = State.CLASSIFY_HATEFUL
                self.report_category = "Hateful Content"
                return ["Please classify the hateful content as either `doxxing`, `bullying`, or `hate speech`."]
            elif "sexual content" in content:
                self.state = State.CLASSIFY_SEXUAL
                self.report_category = "Sexual Content"
                return ["Please classify the sexual content as either `nonconsensual`, `unwanted`, or `child`."]
            elif "spam" in content:
                self.state = State.CLASSIFY_SPAM
                self.report_category = "Spam"
                return ["Please classify the spam as either `spam` or `impersonation`."]
            elif "violent content" in content:
                self.state = State.CLASSIFY_VIOLENT
                self.report_category = "Violent Content"
                return ["Please classify the violent content as either `self harm` or `glorifying violence`."]
            else:
                return ["I'm sorry, I didn't understand that. Please try again or say `cancel` to cancel."]

        if self.state in [State.CLASSIFY_HATEFUL, State.CLASSIFY_SEXUAL, State.CLASSIFY_SPAM, State.CLASSIFY_VIOLENT]:
            if any(keyword in content for keyword in self.HATEFUL_KEYWORDS + self.SEXUAL_KEYWORDS + self.SPAM_KEYWORDS + self.VIOLENT_KEYWORDS):
                self.report_subcategory = content 
                self.state = State.REPORT_DIRECTED_TO
                return ["Thank you for your report. Was this message directed towards `myself`, `a community or group to which I belong`, or `someone else`?"]
            else:
                return ["I'm sorry, I didn't understand that. Please try again or say `cancel` to cancel."]

        if self.state == State.REPORT_DIRECTED_TO:
            if "myself" in content:
                self.directed_to = "myself" 
                reply = "Thank you for your report. Your safety is important to us and we're working hard to make this space safer for you."
            elif "a community" in content or "group" in content:
                self.directed_to = "a community or group to which I belong"
                reply = "Thank you for your report. We're committed to protecting communities from harmful content and behavior."
            elif "someone else" in content:
                self.directed_to = "someone else" 
                reply = "Thank you for your report. We appreciate your help in keeping this space safe for others."
            else:
                return ["I'm sorry, I didn't understand that. Please try again or say `cancel` to cancel."]
                
            self.state = State.REPORT_COMPLETE
            reply += "\n\nYour report about the " + self.report_category + " has been submitted. We will review it shortly."
            return [reply]

        return []

    def report_complete(self):
        return self.state == State.REPORT_COMPLETE

    def generate_summary(self): 
        reply = "" 
        reply += "Report Summary\n" 
        reply += "--------------\n" 
        reply += "Reporter: " + self.reporter.name + "\n"
        reply += "Message: " + self.message.content + "\n" 
        reply += "Author: " + self.message.author.name + "\n" 
        reply += "Channel: " + self.message.channel.name + "\n" 
        reply += "Guild: " + self.message.guild.name + "\n" 
        reply += "Category: " + self.report_category + "\n" 
        reply += "Subcategory: " + self.report_subcategory + "\n" 
        reply += "Directed to: " + self.directed_to + "\n" 
        reply += "Block user: " + str(self.block) + "\n" 
        return reply 
