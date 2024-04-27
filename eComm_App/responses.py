from simple_chatbot.responses import GenericRandomResponse


class GreetingResponse(GenericRandomResponse):
    choices = ("Hey, how can I help you?",
               "Hey friend. How are you? How can I help you?",
               "Hey There, How Can i Help?"
               )

# StudentDetails

class StudentDetails(GenericRandomResponse):
    choices = ("Hey Student!, Can I have your Enrollment no?",
               "Which Stream are you in?,Can I have your Enrollment no?",
               )
    

class GoodbyeResponse(GenericRandomResponse):
    choices = ("See you later.",
               "Thanks for visiting.",
               "See ya! Have a nice day.")