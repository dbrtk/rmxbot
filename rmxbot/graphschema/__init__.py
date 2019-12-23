

import graphene

from ..apps.corpus import queries as corpus_queries


class MutationQuery(graphene.ObjectType):
    pass


class SubscriptionQuery(graphene.ObjectType):
    pass


class TestQuery(graphene.ObjectType):
    # this defines a Field `hello` in our Schema with a single Argument `name`
    hello = graphene.String(name=graphene.String(default_value="stranger"))
    goodbye = graphene.String()

    # our Resolver method takes the GraphQL context (root, info) as well as
    # Argument (name) for the Field and returns data for the query Response

    def resolve_hello(root, info, name):
        return f'Hello {name}!'

    def resolve_goodbye(root, info):
        return 'See ya!'


class Query(corpus_queries.Corpus,
            TestQuery,
            graphene.ObjectType):
    """Defining hte Query that inherits from many objects."""
    pass


schema = graphene.Schema(query=TestQuery)
