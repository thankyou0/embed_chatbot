import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const accessToken = request.cookies.get("access_token");

  // Public routes (no auth required)
  const publicRoutes = [
    "/login",
    "/signup",
    "/forgot-password",
    "/reset-password",
  ];
  const isPublicRoute = publicRoutes.includes(pathname);

  // Auth-only routes (requires auth but not full dashboard access)
  const authOnlyRoutes = ["/change-password"];
  const isAuthOnlyRoute = authOnlyRoutes.includes(pathname);

  // If accessing a protected route without token, redirect to login
  if (
    !isPublicRoute &&
    !isAuthOnlyRoute &&
    !accessToken &&
    pathname.startsWith("/dashboard")
  ) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // If accessing auth-only route without token, redirect to login
  if (isAuthOnlyRoute && !accessToken) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // If accessing login/signup with token, redirect to dashboard
  if (isPublicRoute && accessToken) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/login",
    "/signup",
    "/forgot-password",
    "/reset-password",
    "/change-password",
  ],
};
