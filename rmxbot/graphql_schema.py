import graphene

from .apps.corpus import queries as corpus_queries
from .apps.corpus import mutations as corpus_mutations


corpus_schema = graphene.Schema(
    query=corpus_queries.Query,
    mutation=corpus_mutations.Mutation
)
