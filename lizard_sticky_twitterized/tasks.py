from celery.task import task

from lizard_ui.multitenancy import set_host

from lizard_sticky_twitterized.twitter_connector import search_twitter


@task
def search_twitter_task(*args, **options):
    # Set host for lizard 5 multitenancy.
    if 'host' in options:
        set_host(options['host'])
    search_twitter(*args, **options)
