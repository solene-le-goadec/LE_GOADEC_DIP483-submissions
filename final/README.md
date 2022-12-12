## Final task instructions

You can access the final task here :

This website is an example of how to use the services created for this task.

Here is how the different APIs work :

### Get a suggestion

/search
Use parameter "chars" containing your request. The response is a JSON containing the suggestions as an ordered list.

### Accept a suggestion
Use parameter "name" the suggestion that you accepted. 
Optionnal parameter "url" can be added if you want to be redirected afterwards. 
Otherwise, a JSON confirming the **update of the database** is returned.

### Decline a suggestion

Use the parameters "suggestion" (the declined suggestion) and "name" (the name you wanted to use). 
Optionnal parameter "url" can be added if you want to be redirected afterwards. 
Otherwise, a JSON confirming the **update of the database** is returned.
