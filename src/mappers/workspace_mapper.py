from src.models.workspace import WorkspaceModel
from src.models.workspace_settings import WorkspaceSettingsModel
from src.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from src.schemas.workspace_settings import WorkspaceSettingsCreate


class WorkspaceMapper:
    def workspace_create_map(self, data: WorkspaceCreate) -> WorkspaceModel:
        return WorkspaceModel(
            **data.model_dump(exclude={'workspace_settings'}),
            workspace_settings=self.workspace_settings_create_map(
                data.workspace_settings,
            ),
        )

    def workspace_update_map(
            self,
            data: WorkspaceUpdate,
            workspace: WorkspaceModel,
    ) -> WorkspaceModel:
        update_data = data.model_dump(
            exclude_unset=True,
            exclude={'workspace_settings'},
        )

        if data.workspace_settings is not None:
            settings_data = data.workspace_settings.model_dump(
                exclude_unset=True,
            )
            for field, value in settings_data.items():
                setattr(workspace.workspace_settings, field, value)

        for field, value in update_data.items():
            setattr(workspace, field, value)

        return workspace

    def workspace_settings_create_map(
            self,
            data: WorkspaceSettingsCreate,
    ) -> WorkspaceSettingsModel:
        return WorkspaceSettingsModel(**data.model_dump())

    # получить объект из модели, преобразовать его в схему.
    def workspace_response_map(self, data: WorkspaceModel) -> WorkspaceResponse:
        return WorkspaceResponse.model_validate(data, from_attributes=True)
