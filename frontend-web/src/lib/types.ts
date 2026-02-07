export interface Article {
  id: number;
  Title: string;
  Content: string | null;
  "Image URL": string | null;
  Category: string | null;
  Summary: string | null;
  Tags: string[] | null;
  created_at: string;
}

export function slugify(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)+/g, "");
}

export function unslugify(slug: string): string {
  return slug.replace(/-/g, " ");
}

export const SITE_NAME = "foundersTribe";
export const SITE_DESCRIPTION =
  "Stories, insights, and news about founders and startups.";
export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";
export const ARTICLES_PER_PAGE = 9;
