import { http, HttpResponse, type RequestHandler } from "msw";

export const HEALTH_API_PATH = "/api/v1/health";

export const handlers: RequestHandler[] = [
  http.get(`*${HEALTH_API_PATH}`, () =>
    HttpResponse.json({ status: "ok", schema_revision: "2026-09" }),
  ),
];
