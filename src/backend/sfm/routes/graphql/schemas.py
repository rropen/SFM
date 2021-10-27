import graphene


class WorkItemCategory(graphene.Enum):
    deployment = "Deployment"
    issue = "Issue"
    pull_request = "Pull Request"
    production_defect = "Production Defect"


class WorkItemOutput(graphene.ObjectType):
    id = graphene.Int()
    category = graphene.Field(WorkItemCategory, required=True)
    start_time = graphene.String()
    end_time = graphene.String()
    failed = graphene.Boolean()
    comments = graphene.String()
    issue_num = graphene.Int()
    duration_open = graphene.Int()
    project_id = graphene.Int()

    # project = graphene.Field(ProjectGraph, required=True)
    # commits = graphene.Field(CommitGraph, required=True)


class ProjectOutput(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    repo_url = graphene.String()
    on_prem = graphene.Boolean()
    lead_name = graphene.String()
    lead_email = graphene.String()
    description = graphene.String()
    location = graphene.String()
    github_id = graphene.Int()
