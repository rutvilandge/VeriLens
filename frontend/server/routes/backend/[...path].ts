import { createError, defineEventHandler, getRequestURL, proxyRequest } from "h3";

export default defineEventHandler((event) => {
  const backendOrigin = useRuntimeConfig(event).backendOrigin;
  if (typeof backendOrigin !== "string" || !backendOrigin) {
    throw createError({ statusCode: 503, statusMessage: "Backend API is not configured" });
  }

  let backendUrl: URL;
  try {
    backendUrl = new URL(backendOrigin);
  } catch {
    throw createError({ statusCode: 500, statusMessage: "Backend API URL is invalid" });
  }

  if (!(["https:", "http:"].includes(backendUrl.protocol)) || backendUrl.username || backendUrl.password) {
    throw createError({ statusCode: 500, statusMessage: "Backend API URL is invalid" });
  }

  const requestUrl = getRequestURL(event);
  const backendPath = requestUrl.pathname.replace(/^\/backend(?=\/|$)/, "") || "/";
  const targetUrl = new URL(`${backendPath}${requestUrl.search}`, backendUrl.origin);

  return proxyRequest(event, targetUrl.toString());
});
