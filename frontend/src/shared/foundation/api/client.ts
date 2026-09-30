import createClient, { type Middleware } from "openapi-fetch";
import type { paths } from "./schema";

export interface ProblemDetails {
  type?: string;
  title?: string;
  status: number;
  code?: string;
  detail?: string;
  params?: Record<string, unknown>;
  errors?: Array<{
    in: string;
    path: string;
    code: string;
    params: Record<string, unknown>;
  }>;
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string | undefined;
  readonly detail: string | undefined;
  readonly problem: ProblemDetails;

  constructor(problem: ProblemDetails) {
    super(
      problem.detail ?? problem.title ?? `Request failed (${problem.status}).`,
    );
    this.name = "ApiError";
    this.status = problem.status;
    this.code = problem.code;
    this.detail = problem.detail;
    this.problem = problem;
  }
}

export const API_BASE_URL = "/api";
export const PROBLEM_MEDIA_TYPE = "application/problem+json";

export function mapProblemResponse(
  response: Response,
): Promise<ApiError | null> {
  const contentType = response.headers
    .get("content-type")
    ?.split(";")[0]
    ?.trim();
  if (contentType !== PROBLEM_MEDIA_TYPE) {
    return Promise.resolve(null);
  }

  return response
    .clone()
    .json()
    .then((body: unknown) => {
      if (!isProblemDetails(body)) {
        return null;
      }
      return new ApiError({ ...body, status: response.status });
    });
}

function isProblemDetails(body: unknown): body is ProblemDetails {
  if (typeof body !== "object" || body === null || !("status" in body)) {
    return false;
  }
  return (
    typeof body.status === "number" &&
    (!("title" in body) || typeof body.title === "string") &&
    (!("detail" in body) || typeof body.detail === "string") &&
    (!("code" in body) || typeof body.code === "string")
  );
}

const problemResponseMiddleware: Middleware = {
  async onResponse({ response }) {
    if (response.ok) {
      return undefined;
    }
    const apiError = await mapProblemResponse(response);
    if (apiError) {
      throw apiError;
    }
    return undefined;
  },
};

export const apiClient = createClient<paths>({ baseUrl: API_BASE_URL });
apiClient.use(problemResponseMiddleware);
