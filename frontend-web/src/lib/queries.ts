import { supabase } from "./supabase";
import { Article, ARTICLES_PER_PAGE } from "./types";

const ARTICLE_COLUMNS =
  'id, "Title", "Content", "Image URL", "Category", "Summary", "Tags", created_at';

/**
 * Fetches a paginated list of articles.
 *
 * @param {number} [page=1] - The current page number (1-based index).
 * @param {number} [limit=ARTICLES_PER_PAGE] - Number of articles per page.
 * @returns {Promise<{ articles: Article[]; count: number }>} An object containing the list of articles and the total count.
 */
export async function getArticles(
  page: number = 1,
  limit: number = ARTICLES_PER_PAGE
): Promise<{ articles: Article[]; count: number }> {
  const from = (page - 1) * limit;
  const to = from + limit - 1;

  const { data, count, error } = await supabase
    .from("Articles")
    .select(ARTICLE_COLUMNS, { count: "exact" })
    .order("created_at", { ascending: false })
    .range(from, to);

  if (error) throw error;
  return { articles: (data as Article[]) || [], count: count || 0 };
}

/**
 * Fetches a single article by its slug.
 * The slug is derived from the article title.
 *
 * @param {string} slug - The URL-friendly slug of the article.
 * @returns {Promise<Article | null>} The article object if found, or null otherwise.
 */
export async function getArticleBySlug(
  slug: string
): Promise<Article | null> {
  const { data, error } = await supabase
    .from("Articles")
    .select(ARTICLE_COLUMNS)
    .order("created_at", { ascending: false });

  if (error) throw error;
  if (!data) return null;

  const article = (data as Article[]).find(
    (a) =>
      a.Title.toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/(^-|-$)+/g, "") === slug
  );

  return article || null;
}

/**
 * Fetches paginated articles filtered by category.
 *
 * @param {string} category - The category to filter by.
 * @param {number} [page=1] - The current page number.
 * @param {number} [limit=ARTICLES_PER_PAGE] - Number of articles per page.
 * @returns {Promise<{ articles: Article[]; count: number }>} An object containing the list of filtered articles and the total count.
 */
export async function getArticlesByCategory(
  category: string,
  page: number = 1,
  limit: number = ARTICLES_PER_PAGE
): Promise<{ articles: Article[]; count: number }> {
  const from = (page - 1) * limit;
  const to = from + limit - 1;

  const { data, count, error } = await supabase
    .from("Articles")
    .select(ARTICLE_COLUMNS, { count: "exact" })
    .eq("Category", category)
    .order("created_at", { ascending: false })
    .range(from, to);

  if (error) throw error;
  return { articles: (data as Article[]) || [], count: count || 0 };
}

/**
 * Fetches paginated articles filtered by a specific tag.
 *
 * @param {string} tag - The tag to filter by.
 * @param {number} [page=1] - The current page number.
 * @param {number} [limit=ARTICLES_PER_PAGE] - Number of articles per page.
 * @returns {Promise<{ articles: Article[]; count: number }>} An object containing the list of filtered articles and the total count.
 */
export async function getArticlesByTag(
  tag: string,
  page: number = 1,
  limit: number = ARTICLES_PER_PAGE
): Promise<{ articles: Article[]; count: number }> {
  const from = (page - 1) * limit;
  const to = from + limit - 1;

  const { data, count, error } = await supabase
    .from("Articles")
    .select(ARTICLE_COLUMNS, { count: "exact" })
    .contains("Tags", [tag])
    .order("created_at", { ascending: false })
    .range(from, to);

  if (error) throw error;
  return { articles: (data as Article[]) || [], count: count || 0 };
}

/**
 * Searches for articles matching a query string in the Title or Summary.
 *
 * @param {string} query - The search query term.
 * @param {number} [page=1] - The current page number.
 * @param {number} [limit=ARTICLES_PER_PAGE] - Number of articles per page.
 * @returns {Promise<{ articles: Article[]; count: number }>} An object containing the list of matching articles and the total count.
 */
export async function searchArticles(
  query: string,
  page: number = 1,
  limit: number = ARTICLES_PER_PAGE
): Promise<{ articles: Article[]; count: number }> {
  const from = (page - 1) * limit;
  const to = from + limit - 1;

  const { data, count, error } = await supabase
    .from("Articles")
    .select(ARTICLE_COLUMNS, { count: "exact" })
    .or(`Title.ilike.%${query}%,Summary.ilike.%${query}%`)
    .order("created_at", { ascending: false })
    .range(from, to);

  if (error) throw error;
  return { articles: (data as Article[]) || [], count: count || 0 };
}

/**
 * Retrieves all unique categories from the Articles table.
 *
 * @returns {Promise<string[]>} A sorted list of unique category names.
 */
export async function getAllCategories(): Promise<string[]> {
  const { data, error } = await supabase
    .from("Articles")
    .select("Category")
    .not("Category", "is", null);

  if (error) throw error;
  const categories = [
    ...new Set((data as { Category: string }[]).map((d) => d.Category)),
  ];
  return categories.sort();
}

/**
 * Retrieves all unique tags from the Articles table.
 * Flattens the tags from all articles into a single unique list.
 *
 * @returns {Promise<string[]>} A sorted list of unique tags.
 */
export async function getAllTags(): Promise<string[]> {
  const { data, error } = await supabase
    .from("Articles")
    .select("Tags")
    .not("Tags", "is", null);

  if (error) throw error;
  const tags = new Set<string>();
  (data as { Tags: string[] }[]).forEach((d) => {
    d.Tags?.forEach((t) => tags.add(t));
  });
  return [...tags].sort();
}

/**
 * Retrieves all articles without pagination.
 * Use with caution on large datasets.
 *
 * @returns {Promise<Article[]>} A list of all articles.
 */
export async function getAllArticles(): Promise<Article[]> {
  const { data, error } = await supabase
    .from("Articles")
    .select(ARTICLE_COLUMNS)
    .order("created_at", { ascending: false });

  if (error) throw error;
  return (data as Article[]) || [];
}

/**
 * Fetches related articles based on category, excluding the current article.
 *
 * @param {Article} article - The current article to find related content for.
 * @param {number} [limit=3] - Maximum number of related articles to return.
 * @returns {Promise<Article[]>} A list of related articles.
 */
export async function getRelatedArticles(
  article: Article,
  limit: number = 3
): Promise<Article[]> {
  let query = supabase
    .from("Articles")
    .select(ARTICLE_COLUMNS)
    .neq("id", article.id)
    .order("created_at", { ascending: false })
    .limit(limit);

  if (article.Category) {
    query = query.eq("Category", article.Category);
  }

  const { data, error } = await query;
  if (error) throw error;
  return (data as Article[]) || [];
}
