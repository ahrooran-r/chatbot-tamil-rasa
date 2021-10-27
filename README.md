# chatbot-tamil-rasa
This is a chatbot in Tamil language developed with Rasa

### Introduction

Many users struggle to reload through their carrier’s respective online portals. The main reason being difficult to understand English and code words for reload etc. are not familiar. As a solution, I developed this chatbot to facilitate reload requirements for a user. The bot is developed with *Rasa*.

The bot can reload, cancel last reload, get a refund, get coverage for a particular area etc. in Tamil. Other than that, standard greetings, bot_question and other standard questions can now be asked in Tamil language.

Because the actual backend implementation is not possible (that is not a requirement), I have added outputs based on some randomness. So, for example, reload might be successful or unsuccessful depends on a random True/False result. The actions depend on random execution for most of such user queries so all the outcomes could be emulated.

### Issues I faced during development

1.	Rasa could not detect certain numbers in a statement.
      1. With default pipeline, Rasa could not detect phone number.
      2. But it detected account number and amount correctly.
      2. So, I played a little bot with the pipeline and switched to *RegexEntityExtractor*. It was worse. It detected numbers but did not correctly identify them as correct entities. For example, an *account number* is wrongly slotted into *phone number*.
      2. I have asked the problem in stack overflow, (https://stackoverflow.com/q/69626455/10582056), but no answer
      2. So as an ultimate solution, I have changed regex for *phone*, *account*, and *amount* (Initially there was no regex, I just gave some examples for Rasa to identify correct slots itself) and replaced *RegexEntityExtractor* with *RegexFeaturizer*.
      2. It works now, however in forums they said the inconsistencies in training is common, and sometimes it might not work well.

2.	Sometimes slots are forgotten.
      a.	The culprit is the *MemoizationPolicy*. I changed history to 7 and now it works.
      b.	Also, for *TEDPolicy*, the epochs to train are increased to 200

Also, I have utilized most of Rasa’s core concepts such as *rules*, *actions*, *NLU* and *domain*. Some new things such as *SlotSet* took some time to work out, but eventually I got through it. I have added enough in-code comments to project as well.
