#!/bin/sh -e

POOL_NAME="kb-idp-gh"
PROVIDER_NAME="github"
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
SERVICE_ACCOUNT_NAME="github-actions"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
ORG_NAME="kookaburracodes"
REPO_NAME="kookaburra"

gcloud iam workload-identity-pools create "${POOL_NAME}" \
--project="${PROJECT_ID}" \
--location="global" \
--display-name="Kookaburra GitHub Actions IDP" || true

gcloud iam workload-identity-pools providers create-oidc "${PROVIDER_NAME}" \
--project="${PROJECT_ID}" \
--location="global" \
--workload-identity-pool="${POOL_NAME}" \
--display-name="GitHub Provider" \
--attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.aud=assertion.aud,attribute.repository=assertion.repository" \
--issuer-uri="https://token.actions.githubusercontent.com" || true

gcloud iam service-accounts create "${SERVICE_ACCOUNT_NAME}" \
--project="${PROJECT_ID}" \
--description="GitHub Actions Service Account" \
--display-name="GitHub Actions Service Account"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member="serviceAccount:${SERVICE_ACCOUNT}" \
--role="roles/run.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member="serviceAccount:${SERVICE_ACCOUNT}" \
--role "roles/run.serviceAgent"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member="serviceAccount:${SERVICE_ACCOUNT}" \
--role "roles/storage.admin"

gcloud iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT}" \
--project="${PROJECT_ID}" \
--role="roles/iam.workloadIdentityUser" \
--member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_NAME}/attribute.repository/${ORG_NAME}/${REPO_NAME}"
