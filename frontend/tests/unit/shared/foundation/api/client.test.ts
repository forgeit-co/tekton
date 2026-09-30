import { describe, expect, it } from "vitest";
import {
  ApiError,
  mapProblemResponse,
  PROBLEM_MEDIA_TYPE,
} from "@/shared/foundation/api/client";

describe("mapProblemResponse", () => {
  it("maps problem+json fields into a typed API error", async () => {
    const response = new Response(
      JSON.stringify({
        type: "urn:tekton:error:service.unavailable",
        title: "Service unavailable",
        status: 503,
        code: "service.unavailable",
        detail: "The service is unavailable.",
        params: {},
      }),
      {
        status: 503,
        headers: { "content-type": PROBLEM_MEDIA_TYPE },
      },
    );

    const apiError = await mapProblemResponse(response);

    expect(apiError).toBeInstanceOf(ApiError);
    expect(apiError).toMatchObject({
      name: "ApiError",
      status: 503,
      code: "service.unavailable",
      detail: "The service is unavailable.",
      message: "The service is unavailable.",
    });
  });

  it("leaves responses without the problem media type unmapped", async () => {
    const response = Response.json(
      { detail: "not a problem" },
      { status: 500 },
    );

    await expect(mapProblemResponse(response)).resolves.toBeNull();
  });
});
