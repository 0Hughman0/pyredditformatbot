Hello, everyone. Python newbie here, just started studying it about a month ago. I apologize if this message is long-winded. I want to be sure I’m articulating my thoughts adequately.

I found a video that explains how to code a simple guessing game. Here’s a link to the video: [https://www.mikedane.com/programming-languages/python/guessing-game/](https://www.mikedane.com/programming-languages/python/guessing-game/)

And here’s the code.

    secret_word = "giraffe"
    guess = ""
    guess_count = 0
    guess_limit = 3
    out_of_guesses = False
    
    while guess != secret_word and not(out_of_guesses):
         if guess_count < guess_limit:
              guess = input("Enter a guess: ")
              guess_count += 1
         else:
              out_of_guesses = True
    
    if out_of_guesses:
         print("You Lose!")
    else:
         print("You Win!")
    

&#x200B;

&#x200B;

I want to try to tweak this code, and add a few things to the program. For instance, I want the program to tell the user which guess they’re on. I will change the quantity of guesses to five, instead of three.

If it’s your first guess, the program should say, “Enter Guess #1.”

If you’re wrong, it should inform you, it should tell you how many guesses you have used, and how many you have left. For example:

“That guess was incorrect. One guess out of five used. Please enter Guess #2.”

“That guess was incorrect. Two guesses out of five used. Please enter Guess #3.”

And:

“That guess was also incorrect. You are down to your final guess.”

I’m working on figuring out how to do all of this. I’m not requesting code for this. I’m just letting you know what I plan on doing. However, there is something I want to add, and I **am** asking for assistance.

After I finish writing the above code, I want to offer a hint to the user when they’re down to their final guess. Something like this:

(If the secret word is TREE, for example.)

“You are down to your final guess, so we are going to give you a hint. It’s something that grows, and is probably in your back yard.”

But here’s what is going to get complicated: I want to have a group of secret words, one of which will be selected by the program randomly. For example, let’s say I have a group of ten secret words. I want the program to pick one of them at random, to use for the program.

I haven’t studied random number generation yet, but I will. The problem I see is this:

How do I synchronize the hints with the secret words? In other words, if the program selects a secret word randomly, then how does it fetch the hint that corresponds to that secret word?

I have studied a little bit about dictionaries, and I’m wondering if they can be used for this…or if something else would serve the program better.

So here’s my question: In order to select a secret word randomly, AND have a corresponding hint for it, are dictionaries the best tool to use to do this, or should I use something else? If it’s something else, what do you suggest?

Thank you for taking the time to read this, and for any feedback you care to give.