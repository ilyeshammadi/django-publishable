=====
Django-Publishable
=====

Django library that add to your models the draft/publish features.

Quick start
-----------

1. Add "publishable" to your INSTALLED_APPS setting like this::
    ```python
    
        INSTALLED_APPS = [
            ...
            'publishable',
        ]
    ```
2. Run `python manage.py migrate` to create the publishable models.
3. Try to replicate this with your models:
    ```python
    from django.db import models
    from publishable.models import Publishable, Publisher
    
    # A Publisher is responsible for triggering 
    # the publish all drafts that he contains
    class User(Publisher):
        pass
    
    # Overdide the Publishable to implement the logic
    # of broadcast_need_to_published
    class MyPublishable(Publishable):
        class Meta:
            abstract = True
        
        def broadcast_need_to_published(self):
            """
                This function will return a Draft instance
                then it's up to you select your Publisher
                and add it to it's draft
            """
            draft = super(MyPublishable, self).broadcast_need_to_published()
            chatbot, _ = User.objects.get_or_create(pk=1)
            chatbot.add_draft(draft)
    
    # After setting up your Publishable
    # then inherit from it into the model that you need to receie
    # draft/publish features
    class Article(MyPublishable):
        title = models.CharField(max_length=255)
        content = models.TextField()
    
        comments = models.ManyToManyField('Comment', related_name='comments')
    
        highlighted_comment = models.ForeignKey('Comment', related_name='highlighted_comment', null=True)
    
    
    class Comment(MyPublishable):
        content = models.CharField(max_length=255)
    
    ```
4. By default now all your model will store changes into the draft
    ```python
    # Add changes and publish one model
    >>> a = Article.objects.create()
    >>> a.title = "foo"
    >>> a.publish()
    >>> a.published.title
    foo
    
    # Let's add changes and publish using a publisher
    >>> a.title = "boo"
    >>> a.save()
    >>> a.published.title
    foo
    >>> user = User.objects.get(pk=1)
    >>> user.publish()
    
    # You can track the status of the publishing process
    >>> user.publishing_status
    PUBLISHED
    
    ```
