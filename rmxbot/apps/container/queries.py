"""GraphQL queries."""

import graphene

from . import data


class TxtDatum(graphene.ObjectType):
    """
    Text objects that are contained by instances of the CorpusModel.
    """
    data_id = graphene.String()
    title = graphene.String()
    texthash = graphene.String()
    url = graphene.String()
    file_id = graphene.String()
    title_id = graphene.String()


class ContainerStructure(graphene.ObjectType):
    """
    The basic structure for the corpus, that maps to the one of the
    model/document as it is saved in the database.
    """
    containerid = graphene.String()
    name = graphene.String()
    description = graphene.String()
    created = graphene.DateTime()
    updated = graphene.DateTime()

    urls = graphene.List(TxtDatum)

    active = graphene.Boolean()

    crawl_ready = graphene.Boolean()

    integrity_check_in_progress = graphene.Boolean()
    corpus_ready = graphene.Boolean()

    data_from_files = graphene.Boolean()
    data_from_the_web = graphene.Boolean()


class ContainerData(graphene.ObjectType):
    """
    Returns the corpus data view calling corpus.data.corpus_data.
    Querying the corpus data view:
    ```
    query {
      containerData(
        containerid:"<CONTAINER-ID>"
      ) {
      availableFeats
      texts {
        dataId
        title
        texthash
        url
        fileId
        titleId
      }
      containerid
      name
    }}
    ```
    """
    containerid = graphene.String(required=True)
    available_feats = graphene.List(graphene.Int)
    name = graphene.String()
    texts = graphene.List(TxtDatum, description="list holding text objects")


class ContainerReady(graphene.ObjectType):
    """
    Checks if a corpus is available and ready to compute.

    The graphql query:
    ```
    query{containerReady(
      containerid:"5e00fe205dbae8b568d496b6",
      feats:10
    ) {
      containerid
      requestedFeatures
      busy
      available
      featuresCount
      featureNumber
    }}
    ```
    """
    containerid = graphene.String()
    busy = graphene.Boolean()
    available = graphene.Boolean()
    requested_features = graphene.Int()
    features_count = graphene.List(graphene.Int)
    feature_number = graphene.Int()


class DatasetReady(graphene.ObjectType):
    """Checking if the dataset is ready after a crawl or file upload."""
    containerid = graphene.String()
    ready = graphene.Boolean()


class TextInDataset(graphene.ObjectType):
    """Lists all the texts in the database. Used by the Texts class."""
    id = graphene.String()
    url = graphene.String()
    created = graphene.DateTime()
    title = graphene.String()
    hostname = graphene.String()


class Texts(graphene.ObjectType):
    """
    Returns texts attached to the dataset.

    This is the query:
    ```
    query {
      texts(containerid:"5e00fe205dbae8b568d496b6") {
        containerid
        filesUploadEndpoint
        datatype
        name
        data {
          id
          url
          created
          title
          hostname
        }
      }
    }
    ```
    """
    files_upload_endpoint = graphene.String()
    datatype = graphene.String()
    containerid = graphene.String()
    name = graphene.String()
    data = graphene.List(TextInDataset)


class ContextPhrase(graphene.ObjectType):
    """The structure for sentences with a fileid."""
    # the unique id of the file in the dataset/folder. There is a fileid
    # field on the level of data.models.DataModel
    fileid = graphene.String()
    # a list of sentences
    sentences = graphene.List(graphene.String)


class FeatureContext(graphene.ObjectType):
    """
    Retrieves sentences (from a dataset) that contain one or more feature-word.

    The graphql query:
    ```
    query {
      featureContext(
        containerid:"5dffc8c93e767601249f2fa7",
        words:["earth","remember","dream","call","picture","plane","book",
               "free","spirit","military","gyroscope","seed","fly","pole",
               "nasa","fishbowl","artificial","horizon","cloud","flat"]
      ){
        containerid
        data {
          sentences
          fileid
        }
        success
      }
    }
    ```
    """
    containerid = graphene.String()
    success = graphene.Boolean()
    data = graphene.List(ContextPhrase)


class FileText(graphene.ObjectType):
    """
    For a given containerid and dataid, returns all sentences that are contained
    in the file.
    Graphql query:
    ```
    query {
      fileText(containerid:"<CONTAINER-ID>", dataid:"<DATA-ID>"){
        dataid
        containerid
        length
        text
      }
    }
    ```
    """
    containerid = graphene.String()
    dataid = graphene.String()
    text = graphene.List(graphene.String)
    length = graphene.Int()


class Word(graphene.ObjectType):

    weight = graphene.Float()
    word = graphene.String()


class Feat(graphene.ObjectType):

    # the weight of the feature
    weight = graphene.Float()
    # a feature is a list of weighted words
    feature = graphene.List(Word)


class Doc(graphene.ObjectType):

    dataid = graphene.String()
    fileid = graphene.String()
    url = graphene.String()
    title = graphene.String()
    weight = graphene.Float()

    features = graphene.List(Feat)


class FeaturesWithDocs(graphene.ObjectType):

    docs = graphene.List(Doc)
    features = graphene.List(Word)


class Features(graphene.ObjectType):
    """This class is used to return features for a given dataset and a feature
    number. if features are not available, they will be computed. In this case
    a success-false response is returned with extra params.

    Graphql query:
    ```
    query {
      features(
        containerid:"<CONTAINER-ID>",
        features:25,
        docsperfeat:3,
        featsperdoc:3,
        words:10
      ) {
        containerid
        requestedFeatures
        available
        busy
        retry
        watch
        success
        docs{
          dataid
          features {
            feature{
              word
              weight
            }
            weight
          }
          fileid
          title
          url
        }
        features{
          docs{
            dataid
            title
            url
            weight
          }
          features{
            weight
            word
          }
        }
      }
    }
    ```
    """
    containerid = graphene.String()
    requested_features = graphene.Int()

    available = graphene.Boolean()
    busy = graphene.Boolean()
    retry = graphene.Boolean()
    watch = graphene.Boolean()
    success = graphene.Boolean()

    features = graphene.List(FeaturesWithDocs)
    docs = graphene.List(Doc)


class FeatureNode(graphene.ObjectType):
    """A feature node for the graph."""
    group = graphene.String()
    id = graphene.String()
    type = graphene.String()
    features = graphene.List(Word)


class DocumentNode(graphene.ObjectType):
    """A document node."""
    dataid = graphene.String()
    fileid = graphene.String()
    url = graphene.String()
    title = graphene.String()
    type = graphene.String()
    group = graphene.String()
    id = graphene.String()


class Nodes(graphene.Union):
    """Returns a union of all nodes (features and documents)."""

    class Meta:
        types = (DocumentNode, FeatureNode)

    @classmethod
    def resolve_type(cls, instance, info):

        if instance.get('type') == 'document':
            return DocumentNode
        elif instance.get('type') == 'feature':
            return FeatureNode
        else:
            raise ValueError(instance)


class Edge(graphene.ObjectType):
    """Weighted edges, connections between feature and document nodes."""
    source = graphene.String()
    target = graphene.String()
    weight = graphene.Float()


class GraphInterface(graphene.Interface):
    """
    Interface to the graph. Depending on the graph's availability, this should
    return an adequate data type:
    - Graph if the graph is available;
    - GraphGenerate if the graph is not available and will be generated.

    This endpoint can be used to watch the status of a graph being generated.

    Graphql Query:
    ```
        query{graph(
            containerid:"<CONTAINER-ID>",
            features:12,
            docsperfeat:3,
            featsperdoc:5,
            words:20
        ) {
          containerid
          success
          features
          __typename
          ... on GraphGenerate {
            busy
            retry
            available
          }
          ... on Graph {
            edge {
              weight
              source
              target
            }
            node{
              __typename
              ... on FeatureNode {
                id
                group
                type
                features{
                  word
                  weight
                }
              }
              ... on DocumentNode {
                id
                group
                type
                dataid
                fileid
                title
                url
              }
            }
          }
        }}
    ```
    """
    containerid = graphene.String()
    features = graphene.Int()
    success = graphene.Boolean()

    @classmethod
    def resolve_type(cls, instance, info):

        if instance.get('success'):
            return Graph
        elif not instance.get('success'):
            return GraphGenerate
        else:
            raise RuntimeError(instance)


class Graph(graphene.ObjectType):
    """
    Returns the data to display the graph, these include nodes and edges.
    """
    class Meta:
        interfaces = (GraphInterface, )

    node = graphene.List(Nodes)
    edge = graphene.List(Edge)


class GraphGenerate(graphene.ObjectType):
    """
    Reteruned when the graph isn't available and will be generated.
    """
    class Meta:
        interfaces = (GraphInterface, )

    busy = graphene.Boolean()
    retry = graphene.Boolean()
    available = graphene.Boolean()


class Query(graphene.AbstractType):
    """Query handler."""

    container_data = graphene.Field(
        ContainerData,
        containerid=graphene.String(required=True)
    )

    paginate = graphene.List(
        ContainerStructure,
        start=graphene.Int(),
        limit=graphene.Int()
    )

    container_ready = graphene.Field(
        ContainerReady,
        containerid=graphene.String(),
        feats=graphene.Int()
    )

    crawl_ready = graphene.Field(DatasetReady, containerid=graphene.String())

    text_upload_ready = graphene.Field(
        DatasetReady, containerid=graphene.String())

    texts = graphene.Field(Texts, containerid=graphene.String())

    feature_context = graphene.Field(
        FeatureContext,
        containerid=graphene.String(),
        words=graphene.List(graphene.String)
    )

    file_text = graphene.Field(
        FileText,
        containerid=graphene.String(),
        dataid=graphene.String()
    )

    features = graphene.Field(
        Features,
        containerid=graphene.String(),
        words=graphene.Int(default_value=10),
        features=graphene.Int(default_value=10),
        docsperfeat=graphene.Int(default_value=5),
        featsperdoc=graphene.Int(default_value=3)
    )

    graph = graphene.Field(
        GraphInterface,
        containerid=graphene.String(),
        words=graphene.Int(default_value=10),
        features=graphene.Int(default_value=10),
        docsperfeat=graphene.Int(default_value=5),
        featsperdoc=graphene.Int(default_value=3)
    )

    def resolve_container_data(parent, info, containerid):
        """
        Retrieve data that summarise a corpus/crawl
        :param info:
        :param containerid:
        :return:
        """
        return data.container_data(containerid)

    def resolve_paginate(parent, info, start, limit):
        """
        Paginates the datasets, retrieving a limited number of field for each
        corpus.

        This is the query:
        ```
        query{paginate(start:0, limit:100){
          containerid
          description
          name
          urls{
            dataId
            url
            title
            fileId
            texthash
          }
        }}
        ```
        :param info:
        :param start:
        :param limit:
        :return:
        """
        return data.paginate(start=start, limit=limit)

    def resolve_container_ready(parent, info, containerid, feats):

        return data.container_is_ready(containerid=containerid, feats=feats)

    def resolve_crawl_ready(parent, info, containerid):
        """
        Checks if the crawl is ready.
        Query:
        ```
        query {
          crawlReady(containerid:"5e00fe205dbae8b568d496b6") {
            containerid
            ready
          }
        }
        ```
        :param info:
        :param containerid:
        :return:
        """
        return data.crawl_is_ready(containerid=containerid)

    def resolve_text_upload_ready(parent, info, containerid):
        """
        Checks if the creation of a data set/container from file upload is ready.
        Query:
        ```
        query {
          textUploadReady(containerid:"5e00fe205dbae8b568d496b6") {
            containerid
            ready
          }
        }
        ```
        :param info:
        :param containerid:
        :return:
        """
        return data.file_upload_ready(containerid)

    def resolve_texts(parent, info, containerid):
        """Retrieves texts attached to a dataset."""
        return data.texts(containerid)

    def resolve_feature_context(parent, info, containerid, words):
        """
        Retrieves a context for a feature (list of words).
        :param info:
        :param containerid: the corpus id
        :param words: list of words
        :return:
        """
        return data.lemma_context(containerid=containerid, words=words)

    def resolve_file_text(parent, info, containerid, dataid):

        return data.get_text_file(containerid=containerid, dataid=dataid)

    def resolve_features(parent, info, containerid, words, features, docsperfeat,
                         featsperdoc):
        """
        Retrieves 2 datasets: docs with features, and features with docs.
        If matrices for a given features (number) don't exist, they will be
        computed.
        :param info:
        :param containerid:
        :param words:
        :param features:
        :param docsperfeat:
        :param featsperdoc:
        :return:
        """
        return data.request_features(
            containerid=containerid,
            words=words,
            features=features,
            docsperfeat=docsperfeat,
            featsperdoc=featsperdoc
        )

    def resolve_graph(parent, info, containerid, words, features, docsperfeat,
                      featsperdoc):

        return data.graph(
            containerid=containerid,
            words=words,
            features=features,
            docsperfeat=docsperfeat,
            featsperdoc=featsperdoc
        )
