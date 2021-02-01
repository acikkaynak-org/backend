import graphene
from apps.api.mutations.base import Base
from apps.api.types import Entry
from apps.core.models import Vote as VoteModel


class TYPES(graphene.Enum):
    UP = VoteModel.TYPES.UP
    DOWN = VoteModel.TYPES.DOWN


class Vote(Base):
    """Vote mutation, creates a vote from a currently logged in user to an Entry."""

    class Input:
        to = graphene.Field(Entry)
        type = graphene.Field(TYPES)

    @classmethod
    def mutate_and_get_payload(cls, root, info, to, type):
        """Votes."""
        return Vote()
