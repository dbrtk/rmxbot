

import graphene

from . import data


class Data(graphene.ObjectType):
    """Structure of the data object as it is saved in the db."""
    dataid = graphene.String()
    created = graphene.DateTime()
    updated = graphene.DateTime()
    fileid = graphene.String()
    hashtxt = graphene.String()
    links = graphene.List(graphene.String)
    title = graphene.String()
    url = graphene.String()


class Query(graphene.ObjectType):

    webpage = graphene.Field(Data, dataid=graphene.String())

    def resolve_webpage(parent, info, dataid):
        """
        Qeurying the contents of a document.

        Graphql query:
        ```
        query {
          webpage(dataid:"<DATA-ID>") {
            dataid
            created
            updated
            fileid
            hashtxt
            title
            url
            links
          }
        }
        ```
        :param info:
        :param dataid:
        :return:
        """

        return data.webpage(docid=dataid)


