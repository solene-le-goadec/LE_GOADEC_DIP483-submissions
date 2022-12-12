## Final task instructions

You can access the final task here : https://final-submission-legoadec.et.r.appspot.com/

This website is an example of how to use the services created for this task.

Here is how the different APIs work :

### Get a suggestion

https://final-submission-legoadec.et.r.appspot.com//search

Use parameter "chars" containing your request. The response is a JSON containing the suggestions as an ordered list.

### Accept a suggestion

https://final-submission-legoadec.et.r.appspot.com/accepted

Use parameter "name" the suggestion that you accepted. 
Optionnal parameter "url" can be added if you want to be redirected afterwards. 
Otherwise, a JSON confirming the **update of the database** is returned.

### Decline a suggestion

https://final-submission-legoadec.et.r.appspot.com/declined
Use the parameters "suggestion" (the declined suggestion) and "name" (the name you wanted to use). 
Optionnal parameter "url" can be added if you want to be redirected afterwards. 
Otherwise, a JSON confirming the **update of the database** is returned.
