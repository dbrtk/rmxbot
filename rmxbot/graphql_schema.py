import graphene

from .apps.corpus.queries import Query as CorpusQuery
from .apps.corpus.queries import (
    ContextPhrase, CorpusDataView, CorpusReady, CorpusStructure, DatasetReady,
    Doc, DocumentNode, Edge, Feat, FeatureContext, Features, FeatureNode,
    FeaturesWithDocs, FileText, Graph, GraphBusy, GraphGenerate, TextInDataset,
    Texts, TxtDatum, Word
)
from .apps.corpus.mutations import Mutation as CorpusMutation
from .apps.data.queries import Data
from .apps.data.queries import Query as DataQuery


class Query(CorpusQuery, DataQuery, graphene.ObjectType):

    pass


class Mutation(CorpusMutation, graphene.ObjectType):

    pass


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    types=[ContextPhrase, CorpusDataView, CorpusReady, CorpusStructure,
           DatasetReady, Doc, DocumentNode, Edge, Feat, FeatureContext,
           Features, FeatureNode, FeaturesWithDocs, FileText, Graph, GraphBusy,
           GraphGenerate, TextInDataset, Texts, TxtDatum, Word, Data]
)

