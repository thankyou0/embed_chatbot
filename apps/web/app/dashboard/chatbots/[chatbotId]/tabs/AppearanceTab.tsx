"use client";

import React from "react";
import { Controller, type UseFormReturn } from "react-hook-form";
import { Save, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ButtonSpinner } from "@/components/ui/loading";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { TabsContent } from "@/components/ui/tabs";
import { getAccessToken } from "@/lib/auth";
import type { AppearanceFormData } from "../types";

interface AppearanceTabProps {
  chatbotId: string;
  appearanceError: string | null;
  appearanceSuccessMessage: string | null;
  isSavingAppearance: boolean;
  newSuggestion: string;
  setNewSuggestion: (s: string) => void;
  handleAddSuggestion: () => void;
  handleRemoveSuggestion: (index: number) => void;
  handleAppearanceSubmit: (data: AppearanceFormData) => void;
  fetchAppearance: () => void;
  setAppearanceSuccessMessage: (msg: string | null) => void;
  setAppearanceError: (msg: string | null) => void;
  avatarInputRef: React.RefObject<HTMLInputElement | null>;
  // Form
  form: UseFormReturn<AppearanceFormData>;
  watchedPrimaryColor: string;
  watchedLanguages: string[];
}

export function AppearanceTab({
  chatbotId,
  appearanceError,
  appearanceSuccessMessage,
  isSavingAppearance,
  newSuggestion,
  setNewSuggestion,
  handleAddSuggestion,
  handleRemoveSuggestion,
  handleAppearanceSubmit,
  fetchAppearance,
  setAppearanceSuccessMessage,
  setAppearanceError,
  avatarInputRef,
  form,
  watchedPrimaryColor,
  watchedLanguages,
}: AppearanceTabProps) {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isDirty },
    setValue,
    watch,
  } = form;

  const formData = watch();

  return (
    <TabsContent value="appearance" className="space-y-4">
      {appearanceError && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          {appearanceError}
        </div>
      )}

      <form onSubmit={handleSubmit(handleAppearanceSubmit)}>
        <div className="max-w-4xl">
          {/* Settings Form */}
          <div className="space-y-6">
            {/* General Settings */}
            <Card>
              <CardHeader>
                <CardTitle>General</CardTitle>
                <CardDescription>
                  Basic chatbot appearance settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="header_text">Header Text</Label>
                  <Controller
                    name="header_text"
                    control={control}
                    render={({ field }) => (
                      <Input
                        {...field}
                        id="header_text"
                        placeholder="Chat Support"
                        onChange={(e) => {
                          field.onChange(e.target.value);
                        }}
                      />
                    )}
                  />
                  {errors.header_text && (
                    <p className="text-sm text-red-600 mt-1">
                      {errors.header_text.message}
                    </p>
                  )}
                </div>

                <div>
                  <Label htmlFor="primary_color">Primary Color</Label>
                  <div className="flex gap-2">
                    <input
                      id="primary_color"
                      type="color"
                      value={watchedPrimaryColor || "#3B82F6"}
                      onChange={(e) => {
                        setValue("primary_color", e.target.value, {
                          shouldDirty: true,
                        });
                      }}
                      className="w-16 h-10 p-1 border rounded cursor-pointer"
                    />
                    <Input
                      value={watchedPrimaryColor || ""}
                      onChange={(e) => {
                        setValue("primary_color", e.target.value, {
                          shouldDirty: true,
                        });
                      }}
                      placeholder="#3B82F6"
                      className="flex-1"
                    />
                  </div>
                  {errors.primary_color && (
                    <p className="text-sm text-red-600 mt-1">
                      {errors.primary_color.message}
                    </p>
                  )}
                </div>

                <div>
                  <Label htmlFor="welcome_message">Welcome Message</Label>
                  <Textarea
                    id="welcome_message"
                    {...register("welcome_message")}
                    placeholder="Hi! How can I help you today?"
                    rows={3}
                  />
                </div>

                <div>
                  <Label htmlFor="avatar_url">Avatar URL</Label>
                  <div className="space-y-2">
                    <Input
                      id="avatar_url"
                      {...register("avatar_url")}
                      placeholder="https://example.com/avatar.png"
                    />
                    <input
                      ref={avatarInputRef}
                      type="file"
                      accept="image/*"
                      style={{ display: "none" }}
                      onChange={async (e) => {
                        const file = e.target.files?.[0];
                        if (!file) return;
                        try {
                          const token = getAccessToken();
                          if (!token) return;
                          const API_URL =
                            process.env.NEXT_PUBLIC_API_URL ||
                            "http://localhost:8000";
                          const uploadFormData = new FormData();
                          uploadFormData.append("avatar", file);
                          const res = await fetch(
                            `${API_URL}/api/v1/chatbots/${chatbotId}/avatar`,
                            {
                              method: "POST",
                              headers: {
                                Authorization: `Bearer ${token}`,
                              },
                              body: uploadFormData,
                            },
                          );
                          if (res.ok) {
                            fetchAppearance();
                            setAppearanceSuccessMessage(
                              "Avatar uploaded successfully!",
                            );
                            setTimeout(
                              () => setAppearanceSuccessMessage(null),
                              3000,
                            );
                          } else {
                            const err = await res
                              .json()
                              .catch(() => ({ detail: "Upload failed" }));
                            setAppearanceError(
                              err.detail || "Avatar upload failed",
                            );
                          }
                        } catch (err) {
                          setAppearanceError("Avatar upload error");
                        } finally {
                          if (avatarInputRef.current)
                            avatarInputRef.current.value = "";
                        }
                      }}
                    />
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="w-full"
                      onClick={() => avatarInputRef.current?.click()}
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Custom Avatar
                    </Button>
                  </div>
                </div>

                <div>
                  <Label htmlFor="position">Position</Label>
                  <RadioGroup
                    value={formData.position}
                    onValueChange={(value) =>
                      setValue(
                        "position",
                        value as "bottom-right" | "bottom-left",
                        { shouldDirty: true },
                      )
                    }
                    className="flex gap-6 mt-2"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem
                        value="bottom-left"
                        id="bottom-left"
                      />
                      <Label htmlFor="bottom-left">Bottom Left</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem
                        value="bottom-right"
                        id="bottom-right"
                      />
                      <Label htmlFor="bottom-right">Bottom Right</Label>
                    </div>
                  </RadioGroup>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="offset_x">Offset X (px)</Label>
                    <Controller
                      name="offset_x"
                      control={control}
                      render={({ field }) => (
                        <Input
                          {...field}
                          id="offset_x"
                          type="number"
                          placeholder="0"
                          value={field.value ?? 0}
                          onChange={(e) => {
                            const value =
                              e.target.value === ""
                                ? 0
                                : parseInt(e.target.value, 10) || 0;
                            field.onChange(value);
                          }}
                        />
                      )}
                    />
                    {errors.offset_x && (
                      <p className="text-sm text-red-600 mt-1">
                        {errors.offset_x.message}
                      </p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="offset_y">Offset Y (px)</Label>
                    <Controller
                      name="offset_y"
                      control={control}
                      render={({ field }) => (
                        <Input
                          {...field}
                          id="offset_y"
                          type="number"
                          placeholder="0"
                          value={field.value ?? 0}
                          onChange={(e) => {
                            const value =
                              e.target.value === ""
                                ? 0
                                : parseInt(e.target.value, 10) || 0;
                            field.onChange(value);
                          }}
                        />
                      )}
                    />
                    {errors.offset_y && (
                      <p className="text-sm text-red-600 mt-1">
                        {errors.offset_y.message}
                      </p>
                    )}
                  </div>
                </div>

                {/* Initial Suggestions - merged into general settings */}
                <div className="pt-4 border-t">
                  <Label className="text-sm font-medium">
                    Initial Suggestions
                  </Label>
                  <p className="text-xs text-muted-foreground mt-0.5 mb-2">
                    Suggested questions shown when users open the chat.
                    {watchedLanguages &&
                      watchedLanguages.some((l: string) => l !== "en") && (
                        <span className="block mt-1 text-amber-600 dark:text-amber-400 font-medium">
                          Tip: Write suggestions in{" "}
                          {watchedLanguages
                            .filter((l: string) => l !== "en")
                            .map((l: string) =>
                              l === "hi" ? "Hindi" : "Gujarati",
                            )
                            .join(" and ")}{" "}
                          to match your selected languages.
                        </span>
                      )}
                  </p>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add a suggestion..."
                      value={newSuggestion}
                      onChange={(e) => setNewSuggestion(e.target.value)}
                      onKeyPress={(e) =>
                        e.key === "Enter" &&
                        (e.preventDefault(), handleAddSuggestion())
                      }
                    />
                    <Button
                      type="button"
                      onClick={handleAddSuggestion}
                      size="sm"
                    >
                      Add
                    </Button>
                  </div>
                  {(formData.initial_suggestions || []).length > 0 && (
                    <div className="space-y-2 mt-2">
                      {(formData.initial_suggestions || []).map(
                        (suggestion, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-2 bg-muted rounded"
                          >
                            <span className="text-sm">{suggestion}</span>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => handleRemoveSuggestion(index)}
                              className="h-6 w-6 p-0 text-red-500 hover:text-red-700"
                            >
                              ×
                            </Button>
                          </div>
                        ),
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Personality & Behavior */}
            <Card>
              <CardHeader>
                <CardTitle>Personality & Behavior</CardTitle>
                <CardDescription>
                  Customize how your chatbot responds
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="personality_tone">
                    Conversation Tone
                  </Label>
                  <Controller
                    name="personality_tone"
                    control={control}
                    render={({ field }) => (
                      <RadioGroup
                        value={field.value}
                        onValueChange={(value) => {
                          field.onChange(value);
                          setValue(
                            "personality_tone",
                            value as
                              | "formal"
                              | "casual"
                              | "friendly"
                              | "professional",
                            { shouldDirty: true },
                          );
                        }}
                        className="grid grid-cols-2 gap-4 mt-2"
                      >
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem
                            value="friendly"
                            id="tone-friendly"
                          />
                          <Label
                            htmlFor="tone-friendly"
                            className="cursor-pointer"
                          >
                            Friendly & Warm
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem
                            value="professional"
                            id="tone-professional"
                          />
                          <Label
                            htmlFor="tone-professional"
                            className="cursor-pointer"
                          >
                            Professional
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="casual" id="tone-casual" />
                          <Label
                            htmlFor="tone-casual"
                            className="cursor-pointer"
                          >
                            Casual & Relaxed
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="formal" id="tone-formal" />
                          <Label
                            htmlFor="tone-formal"
                            className="cursor-pointer"
                          >
                            Formal
                          </Label>
                        </div>
                      </RadioGroup>
                    )}
                  />
                </div>

                <div>
                  <Label htmlFor="response_length">Response Length</Label>
                  <Controller
                    name="response_length"
                    control={control}
                    render={({ field }) => (
                      <RadioGroup
                        value={field.value}
                        onValueChange={(value) => {
                          field.onChange(value);
                          setValue(
                            "response_length",
                            value as "concise" | "balanced" | "detailed",
                            { shouldDirty: true },
                          );
                        }}
                        className="flex gap-4 mt-2"
                      >
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem
                            value="concise"
                            id="length-concise"
                          />
                          <Label
                            htmlFor="length-concise"
                            className="cursor-pointer"
                          >
                            Concise
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem
                            value="balanced"
                            id="length-balanced"
                          />
                          <Label
                            htmlFor="length-balanced"
                            className="cursor-pointer"
                          >
                            Balanced
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem
                            value="detailed"
                            id="length-detailed"
                          />
                          <Label
                            htmlFor="length-detailed"
                            className="cursor-pointer"
                          >
                            Detailed
                          </Label>
                        </div>
                      </RadioGroup>
                    )}
                  />
                </div>

                <div>
                  <Label>Supported Languages</Label>
                  <p className="text-xs text-muted-foreground mt-0.5 mb-2">
                    Select which languages your chatbot should respond in.
                    Users can chat in any selected language. At least one
                    must be selected.
                  </p>
                  <Controller
                    name="languages"
                    control={control}
                    render={({ field }) => {
                      const currentLangs: string[] = field.value || ["en"];
                      const toggleLanguage = (lang: string) => {
                        let newLangs: string[];
                        if (currentLangs.includes(lang)) {
                          // Prevent unchecking the last language
                          if (currentLangs.length <= 1) return;
                          newLangs = currentLangs.filter((l) => l !== lang);
                        } else {
                          newLangs = [...currentLangs, lang];
                        }
                        field.onChange(newLangs);
                        setValue(
                          "languages",
                          newLangs as ("en" | "hi" | "gu")[],
                          {
                            shouldDirty: true,
                          },
                        );
                      };
                      return (
                        <div className="flex flex-col gap-3 mt-2">
                          {[
                            {
                              code: "en",
                              label: "English",
                              desc: "Respond in English",
                            },
                            {
                              code: "hi",
                              label: "हिंदी (Hindi)",
                              desc: "Respond in Hindi + romanized Hindi",
                            },
                            {
                              code: "gu",
                              label: "ગુજરાતી (Gujarati)",
                              desc: "Respond in Gujarati + romanized Gujarati",
                            },
                          ].map((lang) => (
                            <label
                              key={lang.code}
                              className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                                currentLangs.includes(lang.code)
                                  ? "border-emerald-500 bg-emerald-50/50 dark:bg-emerald-900/20"
                                  : "border-border hover:border-muted-foreground/30"
                              }`}
                            >
                              <input
                                type="checkbox"
                                checked={currentLangs.includes(lang.code)}
                                onChange={() => toggleLanguage(lang.code)}
                                className="h-4 w-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500"
                              />
                              <div>
                                <span className="text-sm font-medium">
                                  {lang.label}
                                </span>
                                <span className="block text-xs text-muted-foreground">
                                  {lang.desc}
                                </span>
                              </div>
                            </label>
                          ))}
                          {currentLangs.length > 1 && (
                            <p className="text-xs text-muted-foreground bg-muted/50 p-2 rounded">
                              💡 Your bot will auto-detect the user&apos;s
                              language and respond accordingly. It also
                              supports &quot;WhatsApp-style&quot; messages
                              (e.g., &quot;mane products batav&quot; in
                              romanized Gujarati). Languages not selected
                              will be politely declined.
                            </p>
                          )}
                        </div>
                      );
                    }}
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="temperature">
                      Creativity Level (Temperature)
                    </Label>
                    <span className="text-sm text-muted-foreground">
                      {formData.temperature?.toFixed(1) || "0.7"}
                    </span>
                  </div>
                  <Controller
                    name="temperature"
                    control={control}
                    render={({ field }) => (
                      <div className="mt-2">
                        <input
                          type="range"
                          id="temperature"
                          min="0"
                          max="1"
                          step="0.1"
                          value={field.value ?? 0.7}
                          onChange={(e) => {
                            const value = parseFloat(e.target.value);
                            field.onChange(value);
                            setValue("temperature", value, {
                              shouldDirty: true,
                            });
                          }}
                          className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-emerald-600"
                        />
                        <div className="flex justify-between text-xs text-muted-foreground mt-1">
                          <span>Precise (0.0)</span>
                          <span>Balanced (0.5)</span>
                          <span>Creative (1.0)</span>
                        </div>
                      </div>
                    )}
                  />
                </div>

                <div>
                  <Label htmlFor="custom_instructions">
                    Custom Instructions (Optional)
                  </Label>
                  <Textarea
                    id="custom_instructions"
                    {...register("custom_instructions")}
                    placeholder="Add any additional instructions for how the chatbot should behave..."
                    rows={3}
                    className="mt-2"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    These instructions will be added to the chatbot&apos;s
                    system prompt.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Save Button */}
            <div className="flex items-center justify-end gap-3">
              {appearanceSuccessMessage && (
                <span className="text-sm text-green-600 font-medium animate-in fade-in">
                  {appearanceSuccessMessage}
                </span>
              )}
              <Button
                type="submit"
                disabled={isSavingAppearance || !isDirty}
              >
                {isSavingAppearance ? (
                  <>
                    <ButtonSpinner />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </form>
    </TabsContent>
  );
}
