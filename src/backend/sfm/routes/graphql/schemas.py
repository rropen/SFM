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


class CommitOutput(graphene.ObjectType):
    id = graphene.Int()
    sha = graphene.String()
    date = graphene.String()
    message = graphene.String()
    author = graphene.String()
    work_item_id = graphene.String()
    time_to_pull = graphene.Int()


class DeploymentOutput(graphene.ObjectType):
    project_name = graphene.String()
    deployment_dates = graphene.List(graphene.List(graphene.Int))
    performance = graphene.String()
    deployment_dates_description = graphene.String()
    performance_description = graphene.String()


class LeadTimeOutput(graphene.ObjectType):
    lead_time = graphene.Int()
    time_units = graphene.String()
    performance = graphene.String()
    daily_commits = graphene.List(graphene.List(graphene.Int))
    daily_lead_times = graphene.List(graphene.List(graphene.Int))
    project_name = graphene.String()
    lead_time_description = graphene.String()
    performance_description = graphene.String()
    daily_commits_description = graphene.String()
    daily_lead_times_description = graphene.String()


class TimeToRestoreOutput(graphene.ObjectType):
    time_to_restore = graphene.Float()
    performance = graphene.String()
    daily_times_to_restore = graphene.List(graphene.List(graphene.Float))
    project_name = graphene.String()
    time_to_restore_description = graphene.String()
    performance_description = graphene.String()
    daily_times_to_restore_description = graphene.String()


class ChangeFailureRateOutput(graphene.ObjectType):
    change_failure_rate = graphene.Float()
    daily_change_failure_rate = graphene.List(graphene.List(graphene.Float))
    project_name = graphene.String()
    change_failure_rate_description = graphene.String()
    daily_change_failure_rate_description = graphene.String()
