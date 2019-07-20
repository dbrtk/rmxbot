

import graphene

from ..apps.corpus.graph import force_directed_graph
from .corpus import Corpus, DataObject, ForceDirectedGraph

class RootQuery(graphene.ObjectType):

    corpus_all = graphene.Field(Corpus)

    force_directed_graph = graphene.Field(ForceDirectedGraph)

    def resolve_corpus_all(parent, info):

        print("resolving corpus all")
        print(parent)
        print(info)

    def revolve_force_directed_graph(parent, info, *args, **kwds):

        print("resolving features")
        print(parent)
        print(info)
        print(*args)
        print(**kwds)

        # force_directed_graph({
        #     'feats': '',
        #     'docs_pre_feat': '',
        #     'feats_per_doc': '',
        #     'words': '',
        #     'corpusid': ''
        # })


class MutationQuery(graphene.ObjectType):
    pass


class SubscriptionQuery(graphene.ObjectType):
    pass


rmx_schema = graphene.Schema(
    query=RootQuery,
    # mutation=MutationQuery,
    # subscription=SubscriptionQuery
)

