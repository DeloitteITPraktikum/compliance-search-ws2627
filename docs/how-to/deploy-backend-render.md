
# Deploy Backend on Render

## Setup

We use Render Free to host our FastAPI backend as a Docker container.

- Service: compliance-search-ws2627
- Root Directory: backend
- Runtime: Docker
- Port: 8000
- Plan: Free

## Deployment

1. Connect the GitHub repository to Render.
2. Select the branch with the Dockerfile.
3. Set `backend` as the Root Directory.
4. Choose Docker as the runtime and select the Free plan.
5. Add `PORT=8000` under Environment Variables.
6. Deploy the service.

The API key provided by Pascal should be added as an environment variable when needed. It should not be stored in the repository.

## Backend URL

https://compliance-search-ws2627.onrender.com

## Testing

We tested the deployed backend with the following request:

    curl -X POST https://compliance-search-ws2627.onrender.com/ask \
      -H "Content-Type: application/json" \
      -d '{"question":"How often must TLPT run?"}'

The request returned HTTP 200 with the expected JSON response.

We also ran the grader against the Render URL. It completed without format errors, although the scores are still low because the backend currently uses a fixed example answer.

The Docker container has not been tested locally yet.
