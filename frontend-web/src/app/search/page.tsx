import { searchArticles } from "@/lib/queries";
import { ArticleList } from "@/components/ArticleList";
import { Pagination } from "@/components/Pagination";
import { ARTICLES_PER_PAGE } from "@/lib/types";
import type { Metadata } from "next";

interface PageProps {
  searchParams: Promise<{ q?: string; page?: string }>;
}

export async function generateMetadata({ searchParams }: PageProps): Promise<Metadata> {
  const { q } = await searchParams;
  return { title: q ? `Search: ${q}` : "Search" };
}

export default async function SearchPage({ searchParams }: PageProps) {
  const { q, page: pageParam } = await searchParams;
  const query = q || "";
  const page = Number(pageParam) || 1;

  let articles: Awaited<ReturnType<typeof searchArticles>>["articles"] = [];
  let count = 0;

  if (query) {
    const result = await searchArticles(query, page);
    articles = result.articles;
    count = result.count;
  }

  const totalPages = Math.ceil(count / ARTICLES_PER_PAGE);

  return (
    <>
      <div className="mb-8">
          <h1 className="text-3xl font-bold text-black">
            {query ? `Results for "${query}"` : "Search"}
          </h1>
          {query && (
            <p className="mt-2 text-neutral-500">
            {count} result{count !== 1 ? "s" : ""} found
          </p>
        )}
      </div>
      {query ? (
        <>
          <ArticleList articles={articles} />
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            basePath={`/search?q=${encodeURIComponent(query)}`}
          />
        </>
      ) : (
          <p className="text-neutral-400">Enter a search term to find articles.</p>
      )}
    </>
  );
}
