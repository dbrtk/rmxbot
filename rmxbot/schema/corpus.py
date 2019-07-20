

import graphene


class DataObject(graphene.ObjectType):

    data_id = graphene.String()
    file_id = graphene.String()

    file_path = graphene.String()

    texthash = graphene.String()
    file_hash = graphene.String()

    title = graphene.String()
    file_name = graphene.String()

    url = graphene.String()
    text_url = graphene.String()

    checked = graphene.Boolean()


class Corpus(graphene.ObjectType):

    id = graphene.String()

    name = graphene.String()

    description = graphene.String()

    urls = graphene.List(graphene.String,
                         description="urls that belong to that corpus")

    data_objects = graphene.List(DataObject)

    features = graphene.Int()

    features_per_doc = graphene.Int()

    docs_per_feature = graphene.Int()


class ForceDirectedGraph(graphene.ObjectType):

    corpusid = graphene.String()

    # links = graphene.List()
    # nodes = graphene.List()

    # feats = graphene.Int(default_value=10)
    #
    # words = graphene.Int(default_value=10)
    #
    # docs_per_feat = graphene.Int(default_value=5)
    #
    # feats_per_doc = graphene.Int(default_value=3)


#
#
# class Query(graphene.ObjectType):
#
#     corpusid = graphene.String()
#
#     features = graphene.Int()
#     features_per_doc = graphene.Int()
#     docs_per_feature = graphene.Int()
#
#
#
