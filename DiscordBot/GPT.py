import os
import openai
# print(openai.Model.list()) # Can used to verify GPT-4 access

PROMPT = "" 
PROMPT += 'You are a content moderation system. Classify each input into the following categories: hate speech, threats, doxxing, violent speech, sexual harassment, or non-offensive.\n' 
PROMPT += "For hate speech: \n"
PROMPT += "OFFENSIVE: Slut, whore, cunt bitch (those words together, not individually bc they are also interpreted positively online), “fat and ugly”, fatass/fatty/fatso, kys, shemale, words with negative sentiment →  appearance (examples above) , intellect (“dumb”, “stupid”, “retarded”), ethnic/racial slurs\n"
PROMPT += "Edge cases (OFFENSIVE): little bitch, I hate women, shut up bitch, stupid/whiny bitch, dumb hoe, everyone hates you, comparisons to animals - “she is a gorilla” (could also be considered racist)\n"
PROMPT += "NON OFFENSIVE: serving cunt, ok bitch, kms, fat ass, hey bitch/hoe, slay bitch/hoe, that’s my bitch\n"
PROMPT += "For threats: \n"
PROMPT += "OFFENSIVE: I’m going to find her/you and rape/kill her/you, I will kill you, I’m going to murder that [bitch/whore/slut/cunt], I’ll kill any woman that talks to me, I’m going to fuck you, all the women who have rejected me will be punished, I’m going to kill your entire family\n"
PROMPT += "NON OFFENSIVE: I’m going to fuck it up, You’re going to kill it, You’re going to slay, “slay,” I fuck with it/her \n"
PROMPT += "For doxxing: \n"
PROMPT += "OFFENSIVE: Anything involving a phone number or address combined with “call her” “she lives at” “her family” “she works at” “she attends” “school”, any private info (social security number, passwords, credit card number)\n"
PROMPT += "NOT OFFENSIVE: she lives at the gym (ex. “she lives at” not combined with an address or numbers)\n"
PROMPT += "For violent speech: \n"
PROMPT += "OFFENSIVE: It’s bang out the machete, boom in her face and grip her by the neck, I want to rape her until she enjoys it, shove a gun/knife up her ass/pussy, feminists deserves to be shot/raped, she’s asking to be raped dressed like that, Someone should rape her – that would put her in her place, girls wear this and expect not to get raped, I want to beat her senseless, men should hit their wives\n"
PROMPT += "NON OFFENSIVE: She/he/they killed that, She/he/they ate that, She/he/they murdered that, stop killing women, fuck her/me/you/that/it, let’s talk about rape, fuck marital rape \n"  
PROMPT += "For sexual harassment: \n" 
PROMPT += "OFFENSIVE: You look better with your clothes off, She looks like she gets passed around, You’re ugly, No one wants to fuck you, woman moment, men should rule women, women belong in the kitchen, go back to/stay in the kitchen, this is why women don’t deserve rights, she’s ugly with all that makeup off, all women are snakes, women are property\n"
PROMPT += "NON OFFENSIVE: You look gorgeous/beautiful today, you’re so hot, anyone would kill to have you, I want her to sit on my face, she likes cooking in the kitchen, mommy, she owned me, fight for women’s rights\n" 

PROMPT += "Thus, following the above directions, output either hate speech, threats, doxxing, violent speech, sexual harassment, or non-offensive."
def classify_type(text): 
    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
    {"role": "system", "content": PROMPT},

    {"role": "user", "content": "I'm going to kill you."},
    {"role": "assistant", "content": "threats"},

    {"role": "user", "content": text},

    ]
    )
    output = response['choices'][0]['message']['content']
    return output 

def classify_immediate(text): 
    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
    {"role": "system", "content": "You are a content moderation system. The following message has been reported as containing threats/doxxing. Please classify if this needs to be addressed immediately."},
    
    {"role": "user", "content": "I found out you go to San Jose High School, watch out."},
    {"role": "assistant", "content": "yes"},

    {"role": "user", "content": "I will find and kill you."},
    {"role": "assistant", "content": "yes"},

    {"role": "user", "content": "I think this girl goes to San Jose High School."},
    {"role": "assistant", "content": "no"},

    {"role": "user", "content": text},

    ]
    )
    output = response['choices'][0]['message']['content']
    return output 

def classify_target(text): 
    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
    {"role": "system", "content": "You are a content moderation system. The following message has been reported as containing threats/doxxing. Please classify if the message is directed towards the reporter, or someone else."},
    
    {"role": "user", "content": "I found out you go to San Jose High School, watch out."},
    {"role": "assistant", "content": "reporter"},

    {"role": "user", "content": "I think this girl goes to San Jose High School."},
    {"role": "assistant", "content": "someone else"},

    {"role": "user", "content": text},

    ]
    )
    output = response['choices'][0]['message']['content']
    return output 

