import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const accessToken = request.cookies.get("access_token");
  const refreshToken = request.cookies.get("refresh_token");

  // Consider user "authenticated" if either token exists
  // The client-side AuthContext will handle refreshing expired access tokens
  const hasAuth = accessToken || refreshToken;

  // Landing page at "/" is public — no redirect needed
  // Only redirect authenticated users who explicitly navigate to dashboard
  if (pathname === "/" && hasAuth) {
    // Let landing page render; users can click "Dashboard" to go to /dashboard
    return NextResponse.next();
  }

  // Redirect /dashboard to /dashboard/chatbots
  if (pathname === "/dashboard" || pathname === "/dashboard/") {
    return NextResponse.redirect(new URL("/dashboard/chatbots", request.url));
  }

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

  // If accessing a protected route without any token, redirect to login
  if (
    !isPublicRoute &&
    !isAuthOnlyRoute &&
    !hasAuth &&
    pathname.startsWith("/dashboard")
  ) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // If accessing auth-only route without any token, redirect to login
  if (isAuthOnlyRoute && !hasAuth) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // If accessing login/signup with token, redirect directly to chatbots page
  if (isPublicRoute && hasAuth) {
    return NextResponse.redirect(new URL("/dashboard/chatbots", request.url));
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
