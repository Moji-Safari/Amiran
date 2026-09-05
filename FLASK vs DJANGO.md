Flask & Django in Comparison

overally what i felt during the touching the flask environmnet and features was like a shallow version of the Django.it has a pretty light environment and that caused to i ask myself why everything wasn't already built in the known and common framework.

but over course of the time i found out that this framework is a start-up friendly framework which give the chances to make everything by yourself and modify each package or library for your application purposes.

Django already predicts what you will need during the development and already provides those features as built-in modules, but flask let's you to install or define those features by yourself since it does not know what exactly you might and does not give pre defined features that might bee useless in the future and make your app heavy with unnecessary features for you project.

models & ORM:
in django you have a built in models module which can be used to define tables(relations) of the database and also some classes to inherit and use the pre defined methods to interact with db such as fields types or constraints.
in flask there is no such a thing and you need to define using installed packages like SQLalchemy and psycopg(which i used in the tasks). in this package you use the SQL queries to create schemas and you have complete control on architucture of the project.
in Django you should use Django ORM which works as a middle gate between db and django app, but in flask(pyscopg) you only interact with db using pure SQL and your queries are translated to the db language.

views:
in django there is a module for views and it can handle requests and retrive data from db and validate it and store in db it also handles the logic, but in flask these tasks are devided between service(for handling logic), repository(intracting with db), and routes(handling requests).

urls:
urls in django have two levels, project level and app level, each endpoint is defined in the app level url and then guided by the project level urls.py module.
in flask app level url is defined in the routes of each folder and it's guided by the **init**.py module of the app and register class.

settings and congif.py:
settings in django has some pre defined attributes, but we in config it's up to you to define it and specify proper attributes.

running app:
in django after creating the project using django-admin we get a module called manage.py which handles running responsablity, but in flask we should make that module and import a created object of the Flask class.

templates:
they are almost the same and are not predefined in the projects even in Django.

admin panel:
Django has a built in admin panel that can easily be created and manage the db objects by prevelaged users. but there's no such a thing in flask in built in form.

middlewares:
django has dedicated middleware for different purposes, but there is no such a thing for flask you need specific request handlig options on WSGI.

serializers:
in django we define[USING DJANGO DRF framework] a module serializer which gives constraint on sent and receieved request and it limits exposed data to outside world by defined rules. in flask you need to install libraries like Marshmellow which functions on top of you db schema.
