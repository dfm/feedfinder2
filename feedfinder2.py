#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check for feeds at a url."""

from __future__ import print_function

__all__ = ["find_feeds"]

import logging
from twisted.internet import defer, task
import treq
import urlparse
from bs4 import BeautifulSoup


__version__ = "0.0.2b1"


def coerce_url(url):
    url = url.strip()
    if url.startswith("feed://"):
        return "http://{0}".format(url[7:])
    for proto in ["http://", "https://"]:
        if url.startswith(proto):
            return url
    return "http://{0}".format(url)


class FeedFinder(object):

    def __init__(self, user_agent=None, timeout=None):
        if user_agent is None:
            user_agent = "feedfinder2/{0}".format(__version__)
        self.user_agent = user_agent
        self.timeout = timeout

    @defer.inlineCallbacks
    def get_feed(self, url):
        try:
            r = yield treq.get(
                url,
                headers={"User-Agent": self.user_agent},
                timeout=self.timeout)
            text = yield r.text()
        except Exception as e:
            logging.warn("Error while getting '{0}'".format(url))
            logging.warn("{0}".format(e))
            return
        defer.returnValue(text)

    def is_feed_data(self, text):
        data = text.lower()
        if data.count("<html"):
            return False
        return data.count("<rss")+data.count("<rdf")+data.count("<feed")

    @defer.inlineCallbacks
    def is_feed(self, url):
        """Check if this url a feed."""
        text = yield self.get_feed(url)
        if text is None:
            defer.returnValue(False)
        defer.returnValue(self.is_feed_data(text))

    @defer.inlineCallbacks
    def filter_is_feed(self, urls):
        """Filter the urls by those that are feeds."""
        is_feed_check = yield defer.DeferredList(
            [self.is_feed(u) for u in urls])
        defer.returnValue([i[0] for i in zip(urls, is_feed_check) if i[1][1]])

    def is_feed_url(self, url):
        """Check if the url is a feed-ish url."""
        return any(map(url.lower().endswith,
                       [".rss", ".rdf", ".xml", ".atom"]))

    def is_feedlike_url(self, url):
        """Check if it's a feedlike url."""
        return any(map(url.lower().count,
                       ["rss", "rdf", "xml", "atom", "feed"]))


@defer.inlineCallbacks
def find_feeds(url, check_all=False, user_agent=None, timeout=None):
    """Find feeds at a url."""
    finder = FeedFinder(user_agent=user_agent, timeout=timeout)

    # Format the URL properly.
    url = coerce_url(url)

    # Download the requested URL.
    text = yield finder.get_feed(url)
    if text is None:
        defer.returnValue([])

    # Check if it is already a feed.
    if finder.is_feed_data(text):
        defer.returnValue([url])

    # Look for <link> tags.
    logging.info("Looking for <link> tags.")
    tree = BeautifulSoup(text)
    links = []
    for link in tree.find_all("link"):
        if link.get("type") in ["application/rss+xml",
                                "text/xml",
                                "application/atom+xml",
                                "application/x.atom+xml",
                                "application/x-atom+xml"]:
            links.append(urlparse.urljoin(url, link.get("href", "")))

    # Check the detected links.
    urls = yield finder.filter_is_feed(links)
    logging.info("Found {0} feed <link> tags.".format(len(urls)))
    if len(urls) and not check_all:
        defer.returnValue(sort_urls(urls))

    # Look for <a> tags.
    logging.info("Looking for <a> tags.")
    local, remote = [], []
    for a in tree.find_all("a"):
        href = a.get("href", None)
        if href is None:
            continue
        if "://" not in href and finder.is_feed_url(href):
            local.append(href)
        if finder.is_feedlike_url(href):
            remote.append(href)

    # Check the local URLs.
    local = [urlparse.urljoin(url, l) for l in local]
    urls += yield finder.filter_is_feed(local)
    logging.info("Found {0} local <a> links to feeds.".format(len(urls)))
    if len(urls) and not check_all:
        defer.returnValue(sort_urls(urls))

    # Check the remote URLs.
    remote = [urlparse.urljoin(url, l) for l in remote]
    urls += yield finder.filter_is_feed(remote)
    logging.info("Found {0} remote <a> links to feeds.".format(len(urls)))
    if len(urls) and not check_all:
        defer.returnValue(sort_urls(urls))

    # Guessing potential URLs.
    fns = ["atom.xml", "index.atom", "index.rdf", "rss.xml", "index.xml",
           "index.rss"]
    urls += yield finder.filter_is_feed(
        [urlparse.urljoin(url, f) for f in fns])
    defer.returnValue(sort_urls(urls))


def url_feed_prob(url):
    if "comments" in url:
        return -2
    if "georss" in url:
        return -1
    kw = ["atom", "rss", "rdf", ".xml", "feed"]
    for p, t in zip(range(len(kw), 0, -1), kw):
        if t in url:
            return p
    return 0


def sort_urls(feeds):
    return sorted(list(set(feeds)), key=url_feed_prob, reverse=True)


@task.react
@defer.inlineCallbacks
def main(r):
    yield find_feeds("www.preposterousuniverse.com/blog/").addCallback(print)
    yield find_feeds("http://xkcd.com").addCallback(print)
    yield find_feeds("dan.iel.fm/atom.xml").addCallback(print)
    yield find_feeds("dan.iel.fm", check_all=True).addCallback(print)
    yield find_feeds("kapadia.github.io").addCallback(print)
    yield find_feeds("blog.jonathansick.ca").addCallback(print)
    yield find_feeds("asdasd").addCallback(print)
