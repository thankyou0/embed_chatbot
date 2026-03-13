"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";

interface HeaderContent {
  /** Page title — can be plain text or JSX (e.g. breadcrumb links) */
  title: ReactNode;
  /** Optional short description */
  description?: string;
  /** Optional right-side actions (buttons, filters, etc.) */
  actions?: ReactNode;
}

interface HeaderContextType {
  content: HeaderContent | null;
  setContent: (content: HeaderContent | null) => void;
}

const HeaderCtx = createContext<HeaderContextType>({
  content: null,
  setContent: () => {},
});

export function HeaderProvider({ children }: { children: ReactNode }) {
  const [content, setContent] = useState<HeaderContent | null>(null);
  return (
    <HeaderCtx.Provider value={{ content, setContent }}>
      {children}
    </HeaderCtx.Provider>
  );
}

/**
 * Access the header context directly.
 * Call `setContent(...)` in a useEffect to set page-level header info.
 */
export function useHeaderContent() {
  return useContext(HeaderCtx);
}

/**
 * Convenience hook — sets header title / description / actions on mount,
 * clears on unmount.  Re-runs when any dependency changes.
 */
export function usePageHeader(
  title: ReactNode,
  description?: string,
  actions?: ReactNode,
  deps: unknown[] = [],
) {
  const { setContent } = useContext(HeaderCtx);

  useEffect(() => {
    setContent({ title, description, actions });
    return () => setContent(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [setContent, ...deps]);
}
