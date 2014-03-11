#!/usr/bin/python
# (c) Nelen & Schuurmans.  GPL licensed.
from django.core.management.base import BaseCommand
from lizard_sticky_twitterized.twitter_connector import search_twitter


class Command(BaseCommand):
    help = "Query Twitter's search"
    args = "Some hash tags here..."

    def handle(self, *args, **options):
        search_twitter(*args, **options)
