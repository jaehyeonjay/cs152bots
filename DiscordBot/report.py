from enum import Enum, auto
import discord
import re
from GPT import * 

class State(Enum):
    REPORT_START = auto()
    AWAITING_MESSAGE = auto()
    MESSAGE_IDENTIFIED = auto()
    CLASSIFY_MESSAGE_AUTOMATE = auto() 
    AWAIT_APPROVAL = auto() 
    CLASSIFY_MESSAGE = auto()
    CLASSIFY_IMMEDIATE = auto() 
    CLASSIFY_DIRECTED = auto() 
    REPORT_COMPLETE = auto()
    DELETE_MESSAGE = auto() 

class Report:
    START_KEYWORD = "report"
    CANCEL_KEYWORD = "cancel"
    HELP_KEYWORD = "help"
    CLASS_KEYWORDS = ["doxxing", "threats", "hate speech", "violent speech", "sexual harassment"]

    def __init__(self, client):
        self.state = State.REPORT_START
        self.client = client
        self.reporter = None 
        self.message = None
        self.block = None 
        self.target_manual = None 
        self.target = None 
        self.immediate_manual = None 
        self.immediate = None 
        self.type_manual = None 
        self.type = None 
        self.approved = None 
        self.delete = None 

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
            self.state = State.DELETE_MESSAGE
            self.message = message
            return ["I found this message:", "```" + message.author.name + ": " + message.content + "```", \
                    "Do you want to delete this offending message? Please type y/n."] 

        if self.state == State.DELETE_MESSAGE: 
            if content == 'y': 
                self.delete = True 
            elif content == 'n': 
                self.delete = False 
            reply = "Thank you. Do you want to block the user? Please type y/n\n" 
            self.state = State.MESSAGE_IDENTIFIED
            return [reply]
        
        if self.state == State.MESSAGE_IDENTIFIED:
            if content == 'y': 
                reply = "If you wish to block the user who posted this message, follow these steps:\n"
                reply += "1. Right-click on the user's name in the chat.\n"
                reply += "2. Click `Block` in the dropdown menu.\n" 
                reply += "Our automated system is currently analyzing the report. For a summary of our findings, please type in any key.\n"
                self.state = State.CLASSIFY_MESSAGE_AUTOMATE
                self.block = True 
                return [reply]
            elif content == 'n':
                reply = "Our automated system is currently analyzing the report. For a summary of our findings, please type in any key.\n"
                self.state = State.CLASSIFY_MESSAGE_AUTOMATE
                self.block = False 
                return [reply]
        
        if self.state == State.CLASSIFY_MESSAGE_AUTOMATE: 
            self.type = classify_type(self.message.content) 
            if self.type == "threats" or self.type == "doxxing":
                self.immediate = classify_immediate(self.message.content) 
                self.target = classify_target(self.message.content) 
            # generate a summary of the report 
            reply = "Our automated system has analyzed the report and found the following:\n" 
            reply += "Type: " + self.type + "\n" 
            reply += "Immediate: " + (self.immediate if self.immediate is not None else "N/A") + "\n" 
            reply += "Target: " + (self.target if self.target is not None else "N/A") + "\n" 
            reply += "Do you agree with this summary? If yes, your report summary will be sent to the moderation team. Otherwise, we will walk you through manual report workflow. Please type y/n."
            self.state = State.AWAIT_APPROVAL 
            return [reply] 

        if self.state == State.AWAIT_APPROVAL: 
            if content == 'y': 
                self.approved = True 
                self.state = State.REPORT_COMPLETE 
                return ["Thank you for your report. Your report has been sent to the moderation team. You will receive a DM when the moderation team has reviewed your report."]
            elif content == 'n': 
                self.approved = False
                self.state = State.CLASSIFY_MESSAGE 
                return ["Please classify the message as either `doxxing`, `threats`, `hate speech`, `violent speech`, `sexual harassment`."]

        if self.state == State.CLASSIFY_MESSAGE:
            if "doxxing" in content:
                self.type_manual = "doxxing" 
                self.state = State.CLASSIFY_IMMEDIATE 
                return ["Please tell us if this is an immediate threat (y/n)."]
            elif "threats" in content:
                self.type_manual = "threats" 
                self.state = State.CLASSIFY_IMMEDIATE 
                return ["Please tell us if this is an immediate threat (y/n)."] 
            elif "hate speech" in content: 
                self.type_manual = "hate speech" 
                self.state = State.REPORT_COMPLETE
                return ["Thank you for your report. Your report has been sent to the moderation team. You will receive a DM when the moderation team has reviewed your report."]
            elif "violent speech" in content: 
                self.type_manual = "violent speech" 
                self.state = State.REPORT_COMPLETE
                return ["Thank you for your report. Your report has been sent to the moderation team. You will receive a DM when the moderation team has reviewed your report."] 
            elif "sexual harassment" in content: 
                self.type_manual = "sexual harassment" 
                self.state = State.REPORT_COMPLETE
                return ["Thank you for your report. Your report has been sent to the moderation team. You will receive a DM when the moderation team has reviewed your report."]
            else:
                return ["I'm sorry, I didn't understand that. Please try again or say `cancel` to cancel."]

        if self.state == State.CLASSIFY_IMMEDIATE: 
            if content == 'y': 
                self.immediate_manual = True 
                self.state = State.CLASSIFY_DIRECTED
                return ["Please tell us who the message is directed to: `myself`, `someone else`."]
            elif content == 'n': 
                self.immediate_manual = False 
                self.state = State.CLASSIFY_DIRECTED
                return ["Please tell us who the message is directed to: `myself`, `someone else`."]
            else:
                return ["I'm sorry, I didn't understand that. Please try again or say `cancel` to cancel."]

        if self.state == State.CLASSIFY_DIRECTED: 
            if "myself" in content: 
                self.target_manual = "myself" 
                self.state = State.REPORT_COMPLETE
                return ["Thank you for your report. Your report has been sent to the moderation team. You will receive a DM when the moderation team has reviewed your report."]
            elif "someone else" in content: 
                self.target_manual = "someone else" 
                self.state = State.REPORT_COMPLETE
                return ["Thank you for your report. Your report has been sent to the moderation team. You will receive a DM when the moderation team has reviewed your report."]
            else:
                return ["I'm sorry, I didn't understand that. Please try again or say `cancel` to cancel."]

        return []

    def report_complete(self):
        return self.state == State.REPORT_COMPLETE

    def generate_summary(self): 
        reply = "" 
        reply += "=========================================\n"
        reply += "Report Summary\n" 
        reply += "--------------\n" 
        reply += "Reporter: " + self.reporter.name + "\n"
        reply += "Message: " + self.message.content + "\n" 
        reply += "Author: " + self.message.author.name + "\n" 
        reply += "Channel: " + self.message.channel.name + "\n" 
        reply += "Guild: " + self.message.guild.name + "\n" 
        reply += "Does user want to delete message: " + str(self.delete) + "\n"
        reply += "Block user: " + str(self.block) + "\n"  
        reply += "Our automated system has identified the following about the report" + "\n" 
        reply += "\tType: " + self.type + "\n" 
        reply += "\tImmediate: " + str(self.immediate if self.immediate is not None else "N/A") + "\n" 
        reply += "\tTarget: " + str(self.target if self.target is not None else "N/A") + "\n" 
        reply += "The user agrees with our findings: " + str(self.approved) + "\n" 
        if not self.approved: 
            reply += "The user has classified the report as follows:\n" 
            reply += "\tType: " + self.type_manual + "\n" 
            reply += "\tImmediate: " + str(self.immediate_manual if self.immediate_manual is not None else "N/A") + "\n" 
            reply += "\tTarget: " + str(self.target_manual if self.target_manual is not None else "N/A") + "\n" 
        self.delete = self.delete and self.type != "non-offensive"
        return reply 

