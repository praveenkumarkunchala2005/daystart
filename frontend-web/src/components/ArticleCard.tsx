import Link from "next/link";
import { Article, slugify } from "@/lib/types";
import { CategoryBadge } from "./CategoryBadge";
import { format } from "date-fns";

/**
 * Card component for displaying a summary of an article.
 * Used in lists and grids. Includes image, category, title, and tags.
 *
 * @param {Object} props - Component props.
 * @param {Article} props.article - The article data to display.
 */
export function ArticleCard({ article }: { article: Article }) {
  const slug = slugify(article.Title);

  return (
    <article className="group flex flex-col overflow-hidden rounded-md border border-neutral-200 bg-white transition-shadow hover:shadow-md">
        <Link href={`/article/${slug}`} className="block overflow-hidden bg-black">
          {article["Image URL"] && article["Image URL"].trim() !== "" ? (
            <img
              src={article["Image URL"]}
              alt={article.Title}
              className="h-48 w-full object-cover transition-transform duration-300 group-hover:scale-105 bg-black"
            />
          ) : (
            <div className="flex h-48 items-center justify-center bg-black text-neutral-500">
              <span className="text-lg font-semibold">fT</span>
            </div>
          )}
      </Link>
      <div className="flex flex-1 flex-col p-5">
        <div className="mb-2 flex items-center gap-3">
          {article.Category && <CategoryBadge category={article.Category} />}
          <time className="text-xs text-neutral-400" dateTime={article.created_at} suppressHydrationWarning>
              {format(new Date(article.created_at), "MMM d, yyyy")}
            </time>
        </div>
        <Link href={`/article/${slug}`}>
          <h3 className="mb-2 text-lg font-semibold leading-snug text-black transition-colors group-hover:text-neutral-600">
            {article.Title}
          </h3>
        </Link>
        {article.Summary && (
          <p className="mb-4 line-clamp-2 flex-1 text-sm leading-relaxed text-neutral-500">
            {article.Summary}
          </p>
        )}
        {article.Tags && article.Tags.length > 0 && (
          <div className="mt-auto flex flex-wrap gap-1.5">
            {article.Tags.slice(0, 3).map((tag) => (
              <Link
                key={tag}
                href={`/tag/${encodeURIComponent(tag)}`}
                className="rounded-md bg-neutral-100 px-2.5 py-0.5 text-xs text-neutral-500 transition-colors hover:bg-black hover:text-white"
              >
                #{tag}
              </Link>
            ))}
          </div>
        )}
      </div>
    </article>
  );
}
