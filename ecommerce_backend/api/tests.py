

from api.documents import ProductDocument
from elasticsearch_dsl import Q
search_query = Q(
    "multi_match",
    query="phone",
    fields=["name", "description", "category", "brand"],
    operator="and",
)


filters = Q("range", marked_price={"lte": 60000})  

final_query = search_query & filters
results = ProductDocument.search().query(final_query)
for result in results.execute():
    print(result.to_dict())
