"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import Link from "next/link";
import { SectionLoader, ButtonSpinner } from "@/components/ui/loading";
import { AuthLayout, AuthLayoutSkeleton } from "@/components/auth/AuthLayout";
import { KeyRound } from "lucide-react";
import { apiRequest } from "@/lib/api";

const resetPasswordSchema = z
  .object({
    newPassword: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .max(100, "Password is too long"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;

interface ResetPasswordResponse {
  message: string;
}

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  });

  useEffect(() => {
    const tokenFromUrl = searchParams.get("token");
    if (!tokenFromUrl) {
      setError(
        "Invalid or missing reset token. Please request a new password reset."
      );
      return;
    }
    setToken(tokenFromUrl);
  }, [searchParams]);

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) {
      setError("Invalid reset token. Please request a new password reset.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSubmitting(true);

    try {
      const response = await apiRequest<ResetPasswordResponse>(
        "/api/v1/auth/reset-password",
        {
          method: "POST",
          body: JSON.stringify({
            token,
            new_password: data.newPassword,
          }),
        }
      );

      setSuccess(response.message);
      reset(); // Clear the form

      // Redirect to login after 3 seconds
      setTimeout(() => {
        router.push("/login");
      }, 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!token && !error) {
    return <AuthLayoutSkeleton />;
  }

  return (
    <AuthLayout
      icon={<KeyRound className="h-7 w-7 text-white" />}
      title="Reset Password"
      description="Enter your new password below."
    >
        <form onSubmit={handleSubmit(onSubmit)}>
          <CardContent className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            {success && (
              <Alert>
                <AlertDescription className="text-green-700 dark:text-green-300">
                  {success}
                  <br />
                  <span className="text-sm">Redirecting to login page...</span>
                </AlertDescription>
              </Alert>
            )}
            {!error && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="newPassword">New Password</Label>
                  <Input
                    id="newPassword"
                    type="password"
                    placeholder="••••••••"
                    {...register("newPassword")}
                    disabled={isSubmitting || success !== null}
                  />
                  {errors.newPassword && (
                    <p className="text-sm text-destructive">
                      {errors.newPassword.message}
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm New Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="••••••••"
                    {...register("confirmPassword")}
                    disabled={isSubmitting || success !== null}
                  />
                  {errors.confirmPassword && (
                    <p className="text-sm text-destructive">
                      {errors.confirmPassword.message}
                    </p>
                  )}
                </div>
              </>
            )}
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            {!error && (
              <Button
                type="submit"
                className="w-full"
                disabled={isSubmitting || success !== null}
              >
                {isSubmitting ? (<><ButtonSpinner />Resetting...</>) : "Reset Password"}
              </Button>
            )}
            <div className="flex flex-col space-y-2 text-sm text-center text-muted-foreground">
              <p>
                Remember your password?{" "}
                <Link href="/login" className="text-primary hover:underline">
                  Sign in
                </Link>
              </p>
              <p>
                Need a new reset link?{" "}
                <Link
                  href="/forgot-password"
                  className="text-primary hover:underline"
                >
                  Request new link
                </Link>
              </p>
            </div>
          </CardFooter>
        </form>
    </AuthLayout>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={<AuthLayoutSkeleton />}
    >
      <ResetPasswordForm />
    </Suspense>
  );
}
