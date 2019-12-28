import graphene

from .apps.container.queries import Query as CorpusQuery
from .apps.container.queries import (
    ContextPhrase, CorpusDataView, CorpusReady, CorpusStructure, DatasetReady,
    Doc, DocumentNode, Edge, Feat, FeatureContext, Features, FeatureNode,
    FeaturesWithDocs, FileText, Graph, GraphBusy, GraphGenerate, TextInDataset,
    Texts, TxtDatum, Word
)
from .apps.container.mutations import Mutation as CorpusMutation
from .apps.data.queries import Data
from .apps.data.queries import Query as DataQuery


class RootQuery(CorpusQuery, DataQuery, graphene.ObjectType):

    pass


class Mutation(CorpusMutation, graphene.ObjectType):

    pass


schema = graphene.Schema(
    query=RootQuery,
    mutation=Mutation,
    types=[ContextPhrase, CorpusDataView, CorpusReady, CorpusStructure,
           DatasetReady, Doc, DocumentNode, Edge, Feat, FeatureContext,
           Features, FeatureNode, FeaturesWithDocs, FileText, Graph, GraphBusy,
           GraphGenerate, TextInDataset, Texts, TxtDatum, Word, Data]
)

