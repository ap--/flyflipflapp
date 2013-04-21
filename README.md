
## flyflipflapp

a gtk3 fly flipping scheduler with a google calendar backend.

### current state

initial development started.

### TODO

* [done] get abstraction layer for new google calendar api (v3) up and running
* fine tune addflyevent
* [done] add reminders!
* [done] write gtk3 app
* write android app for simple flystock managing

### Notes

* the reminder system works fine for stocks (recurringEvents). But since google doesn't support reminders after an event started, the only way to get the right behaviour is to add specific events for crosses...

