import { getArticlesByCategory } from "@/lib/queries";
import { ArticleList } from "@/components/ArticleList";
import { Pagination } from "@/components/Pagination";
import { ARTICLES_PER_PAGE } from "@/lib/types";
import type { Metadata } from "next";

interface PageProps {
  params: Promise<{ category: string }>;
  searchParams: Promise<{ page?: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { category } = await params;
  const decoded = decodeURIComponent(category);
  return { title: decoded };
}

export default async function CategoryPage({ params, searchParams }: PageProps) {
  const { category } = await params;
  const { page: pageParam } = await searchParams;
  const decoded = decodeURIComponent(category);
  const page = Number(pageParam) || 1;
  const { articles, count } = await getArticlesByCategory(decoded, page);
  const totalPages = Math.ceil(count / ARTICLES_PER_PAGE);

  return (
    <>
      <div className="mb-8">
          <h1 className="text-3xl font-bold text-black">{decoded}</h1>
          <p className="mt-2 text-neutral-500">
          {count} article{count !== 1 ? "s" : ""} in this category
        </p>
      </div>
      <ArticleList articles={articles} />
      <Pagination
        currentPage={page}
        totalPages={totalPages}
        basePath={`/category/${encodeURIComponent(decoded)}`}
      />
    </>
  );
}
