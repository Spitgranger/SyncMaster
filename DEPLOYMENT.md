The following are intructions for how to deploy the SyncMaster Application:

[Create an AWS account](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) if you do not already have one and log in.

# Backend: Deploy Local Changes

* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed
* [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) (AWS SAM) installed
* [Create an SSO profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html) named SyncMaster
* [Docker](https://www.docker.com/get-started/) Installed
* [uv](https://docs.astral.sh/uv/getting-started/installation/) Installed
* Log in to SyncMaster SSO profile using `aws sso login --profile SyncMaster`
* Build the backend using `bash ./scripts/backend/build.sh`
* Deploy the backend using `bash ./scripts/backend/deploy.sh`

# Frontend: Deploy Local Changes

No way to deploy local changes to cloud, can only test locally

# Backend: Deploy From GitHub

* [Create access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) permitting deployment
* [Create GitHub secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions) for the access keys under `AWS_ACCESS_KEY` and `AWS_ACCESS_KEY_SECRET`
* Push a change to the backend, to the main branch, and it will deploy

# Frontend: Deploy From GitHub

The frontend uses AWS Amplify, which automatically deploys the latest changes from a given branch.
To do an initial setup of the Amplify infrastructure, you can follow these steps:

* Deploy the backend (using either previous method) and record the API base url
* [Create a GitHub PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token) with permissions ???????
* [Create access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) permitting deployment
* [Create GitHub secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions) for the access keys under `BASE_API_URL`, `PAT`, `AWS_ACCESS_KEY` and `AWS_ACCESS_KEY_SECRET`
* Push a change to infrastructure/frontend.yaml on main, for the application to deploy
