import Link from "next/link";
import { Article, slugify } from "@/lib/types";
import { CategoryBadge } from "./CategoryBadge";
import { format } from "date-fns";

/**
 * Hero component for displaying the main featured article.
 * Displays a large background image, category badge, and title.
 *
 * @param {Object} props - Component props.
 * @param {Article} props.article - The article data to display.
 */
export function HeroBanner({ article }: { article: Article }) {
  const slug = slugify(article.Title);

  return (
    <section className="relative mb-12 overflow-hidden rounded-md bg-black">
        <div className="absolute inset-0 bg-black">
          {article["Image URL"] && article["Image URL"].trim() !== "" ? (
            <img
              src={article["Image URL"]}
              alt={article.Title}
              className="h-full w-full object-cover opacity-30 bg-black"
            />
          ) : (
            <div className="h-full w-full bg-black" />
          )}
      </div>
      <div className="relative z-10 flex min-h-[400px] flex-col justify-end p-8 sm:p-12">
        <div className="mb-4 flex items-center gap-3">
          {article.Category && (
            <CategoryBadge category={article.Category} variant="light" />
          )}
            <time className="text-sm text-neutral-400" dateTime={article.created_at} suppressHydrationWarning>
            {format(new Date(article.created_at), "MMMM d, yyyy")}
          </time>
        </div>
        <Link href={`/article/${slug}`}>
          <h1 className="mb-4 max-w-3xl text-3xl font-bold leading-tight text-white transition-colors hover:text-neutral-300 sm:text-4xl lg:text-5xl">
            {article.Title}
          </h1>
        </Link>
        {article.Summary && (
          <p className="mb-6 max-w-2xl text-lg leading-relaxed text-neutral-400">
            {article.Summary}
          </p>
        )}
        <Link
          href={`/article/${slug}`}
          className="inline-flex w-fit items-center gap-2 rounded-md bg-white px-6 py-3 text-sm font-semibold text-black transition-colors hover:bg-neutral-200"
        >
          Read Article
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </Link>
      </div>
    </section>
  );
}
