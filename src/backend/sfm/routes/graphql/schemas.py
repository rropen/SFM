import graphene


class WorkItemCategoryGraph(graphene.Enum):
    deployment = "Deployment"
    issue = "Issue"
    pull_request = "Pull Request"
    production_defect = "Production Defect"


class WorkItemGraph(graphene.ObjectType):
    id = graphene.Int()
    category = graphene.Field(WorkItemCategoryGraph, required=True)
    start_time = graphene.String()
    end_time = graphene.String()
    failed = graphene.Boolean()
    comments = graphene.String()
    issue_num = graphene.Int()
    duration_open = graphene.Int()
    project_id = graphene.Int()

    # project = graphene.Field(ProjectGraph, required=True)
    # commits = graphene.Field(CommitGraph, required=True)
