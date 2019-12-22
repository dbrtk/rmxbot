"""GraphQL queries."""

import graphene

from . import data


class UpdateCrawl(graphene.ObjectType):

    corpusid = graphene.String(required=True)
    endpoint = graphene.String(required=True)
    crawl = graphene.Boolean(default_value=True)


class LaunchCrawl(graphene.ObjectType):

    the_name = graphene.String(required=True)
    endpoint = graphene.String(required=True)
    crawl = graphene.Boolean(default_value=True)


class CorpusDataView(graphene.ObjectType):

    corpusid = graphene.String(required=True)


class Corpus(graphene.ObjectType):

    create_from_crawl = graphene.Field(LaunchCrawl)

    crawl = graphene.Field(UpdateCrawl)

    corpus_data_view = graphene.Field()

    def resolve_create_from_crawl(parent, info, the_name, endpoint, crawl):

        return 'create from crawl called'

    def resolve_crawl(parent, info, corpusid, endpoint, crawl):

        return 'crawl called'

    def resolve_corpus_data_view(parent, info):

        return 'pferdle sucks good'

