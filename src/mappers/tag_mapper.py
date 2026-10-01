from src.models.tag import Tag
from src.schemas.tag import TagResponse, TagUpdate, TagCreate


class TagMapper:
    def tag_response_map(self, tag: Tag) -> TagResponse:
        return TagResponse.model_validate(tag, extra='ignore')

    def tag_create_map(self, data: TagCreate) -> Tag:
        return Tag(**data.model_dump())

    def tag_update_map(self, data: TagUpdate, tag: Tag) -> Tag:
        update_tag = data.model_dump(exclude_unset=True)

        for item, value in update_tag.items():
            setattr(tag, item, value)

        return tag
        