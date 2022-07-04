from .admin import IsAdmin
from loader import dispatcher

if __name__ == "filters":
    dispatcher.filters_factory.bind(IsAdmin)
